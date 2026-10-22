# -*- coding: utf-8 -*-
"""
Core Control-Flow Deobfuscator for PJOrion protected Python 2.7 bytecode.
Reconstructs basic blocks, eliminates dead jumps/forwarders, and reassembles valid bytecodes.
"""

import io
import queue as Queue
import collections
import networkx as nx
from xdis.opcodes import opcode_27 as dis
from xdis import marsh


class Instruction(object):
    def __init__(self, opcode, arg, size):
        self.opcode = opcode
        self.arg = arg
        self.size = size
        self.argval = arg
        self.mnemonic = dis.opname[self.opcode]

    def is_opcode_valid(self):
        return self.opcode in dis.opmap.values()

    def is_ret(self):
        return self.opcode == dis.opmap['RETURN_VALUE']

    def is_control_flow(self):
        cf_ins = (
            'JUMP_IF_FALSE_OR_POP', 'JUMP_IF_TRUE_OR_POP', 'JUMP_ABSOLUTE',
            'POP_JUMP_IF_FALSE', 'POP_JUMP_IF_TRUE', 'CONTINUE_LOOP',
            'FOR_ITER', 'JUMP_FORWARD'
        )
        return self.mnemonic in cf_ins

    def is_conditional(self):
        conditional_ins = (
            'JUMP_IF_FALSE_OR_POP', 'JUMP_IF_TRUE_OR_POP',
            'POP_JUMP_IF_FALSE', 'POP_JUMP_IF_TRUE', 'FOR_ITER'
        )
        return self.is_control_flow() and self.mnemonic in conditional_ins

    def is_unconditional(self):
        unconditional_ins = ('JUMP_ABSOLUTE', 'JUMP_FORWARD', 'CONTINUE_LOOP')
        return self.is_control_flow() and self.mnemonic in unconditional_ins

    def has_xref(self):
        return self.mnemonic in ('SETUP_LOOP', 'SETUP_EXCEPT', 'SETUP_FINALLY', 'SETUP_WITH')

    def assemble(self):
        if self.size == 1:
            return bytes([self.opcode])
        return bytes([self.opcode, self.arg & 0xFF, (self.arg >> 8) & 0xFF])


class Decoder(object):
    def __init__(self, ins_bytes):
        self.ins_bytes = ins_bytes

    def decode_at(self, offset):
        if offset >= len(self.ins_bytes):
            return Instruction(-1, None, 1)

        opcode = self.ins_bytes[offset]
        if opcode not in dis.opmap.values():
            return Instruction(-1, None, 1)

        if opcode < dis.HAVE_ARGUMENT:
            return Instruction(opcode, None, 1)

        if offset + 2 >= len(self.ins_bytes):
            return Instruction(-1, None, 1)

        arg = (self.ins_bytes[offset + 2] << 8) | self.ins_bytes[offset + 1]
        return Instruction(opcode, arg, 3)


class BasicBlock(object):
    def __init__(self):
        self.address = 0
        self.instructions = []
        self.has_xrefs_to = False
        self.xref_instructions = []
        self.b_seen = False

    def add_instruction(self, ins):
        self.instructions.append(ins)

    def instruction_iter(self):
        for ins in self.instructions:
            yield ins

    def size(self):
        return sum(ins.size for ins in self.instructions)


class Disassembler(object):
    def __init__(self, ins_bytes, entrypoint):
        self.ins_bytes = ins_bytes
        self.entrypoint = entrypoint
        self.leaders = None
        self.bb_graph = nx.DiGraph()

    def get_next_ins_addresses(self, ins, addr):
        next_addresses = {}
        if ins.mnemonic in ('JUMP_IF_FALSE_OR_POP', 'JUMP_IF_TRUE_OR_POP', 'POP_JUMP_IF_FALSE', 'POP_JUMP_IF_TRUE'):
            next_addresses['implicit'] = addr + ins.size
            next_addresses['explicit'] = ins.arg
        elif ins.mnemonic in ('JUMP_ABSOLUTE', 'CONTINUE_LOOP'):
            next_addresses['explicit'] = ins.arg
        elif ins.mnemonic == 'FOR_ITER':
            next_addresses['implicit'] = addr + ins.size
            next_addresses['explicit'] = addr + ins.size + ins.arg
        elif ins.mnemonic == 'JUMP_FORWARD':
            next_addresses['explicit'] = addr + ins.size + ins.arg
        elif ins.mnemonic == 'RETURN_VALUE':
            pass
        else:
            next_addresses['implicit'] = addr + ins.size
        return next_addresses

    def get_ins_xref(self, ins, addr):
        xref_ins = {dis.opmap[x] for x in ('SETUP_LOOP', 'SETUP_EXCEPT', 'SETUP_FINALLY', 'SETUP_WITH')}
        if ins.opcode in xref_ins:
            return addr + ins.size + ins.arg
        return None

    def find_leaders(self):
        Leader = collections.namedtuple('Leader', ['address', 'type'])
        leader_set = set()
        leader_set.add(Leader(self.entrypoint, 'S'))

        analysis_q = Queue.Queue()
        analysis_q.put(self.entrypoint)
        already_analyzed = set()
        dec = Decoder(self.ins_bytes)

        while not analysis_q.empty():
            addr = analysis_q.get()
            while True:
                if addr >= len(self.ins_bytes) or addr in already_analyzed:
                    break
                ins = dec.decode_at(addr)
                already_analyzed.add(addr)

                if ins.is_ret():
                    leader_set.add(Leader(addr, 'E'))
                    break

                if ins.is_control_flow():
                    leader_set.add(Leader(addr, 'E'))
                    for target in self.get_next_ins_addresses(ins, addr).values():
                        leader_set.add(Leader(target, 'S'))
                        if target not in already_analyzed:
                            analysis_q.put(target)
                    break
                else:
                    xref = self.get_ins_xref(ins, addr)
                    next_addr = list(self.get_next_ins_addresses(ins, addr).values())
                    if len(next_addr) != 1:
                        break
                    addr = next_addr[0]
                    if xref is not None:
                        leader_set.add(Leader(xref, 'S'))
                        if xref not in already_analyzed:
                            analysis_q.put(xref)

        self.leaders = sorted(leader_set, key=lambda x: (x.address, 0 if x.type == 'S' else 1))

    def construct_basic_blocks(self):
        idx = 0
        dec = Decoder(self.ins_bytes)
        while idx < len(self.leaders):
            if idx + 1 >= len(self.leaders):
                break
            leader1, leader2 = self.leaders[idx], self.leaders[idx + 1]
            addr1, addr2 = leader1.address, leader2.address
            bb = BasicBlock()
            bb.address = addr1
            offset = 0

            if addr1 == self.entrypoint:
                self.bb_graph.add_node(bb, isEntry=True)
            else:
                self.bb_graph.add_node(bb)

            if leader1.type == 'S' and leader2.type == 'E':
                while addr1 + offset <= addr2:
                    ins = dec.decode_at(addr1 + offset)
                    bb.add_instruction(ins)
                    offset += ins.size
                idx += 2
            elif leader1.type == 'S' and leader2.type == 'S':
                while addr1 + offset < addr2:
                    ins = dec.decode_at(addr1 + offset)
                    bb.add_instruction(ins)
                    offset += ins.size
                idx += 1
            else:
                idx += 1

    def find_bb_by_address(self, address):
        for bb in self.bb_graph.nodes():
            if bb.address == address:
                return bb
        return None

    def build_bb_edges(self):
        for bb in list(self.bb_graph.nodes()):
            offset = 0
            for idx in range(len(bb.instructions)):
                ins = bb.instructions[idx]
                xref = self.get_ins_xref(ins, bb.address + offset)
                if xref is not None:
                    xref_bb = self.find_bb_by_address(xref)
                    if xref_bb:
                        ins.argval = xref_bb
                        xref_bb.has_xrefs_to = True
                        xref_bb.xref_instructions.append(ins)

                next_ins_addr = self.get_next_ins_addresses(ins, bb.address + offset)
                if idx == len(bb.instructions) - 1:
                    if ins.is_unconditional():
                        if 'explicit' in next_ins_addr:
                            target_bb = self.find_bb_by_address(next_ins_addr['explicit'])
                            if target_bb:
                                ins.argval = target_bb
                                self.bb_graph.add_edge(bb, target_bb, edge_type='explicit')
                    elif ins.is_conditional():
                        if len(next_ins_addr) == 2:
                            target1_bb = self.find_bb_by_address(next_ins_addr['implicit'])
                            target2_bb = self.find_bb_by_address(next_ins_addr['explicit'])
                            if target1_bb and target2_bb:
                                ins.argval = target2_bb
                                self.bb_graph.add_edge(bb, target1_bb, edge_type='implicit')
                                self.bb_graph.add_edge(bb, target2_bb, edge_type='explicit')
                    elif ins.is_ret():
                        nx.set_node_attributes(self.bb_graph, {bb: {'isTerminal': True}})
                    else:
                        if 'implicit' in next_ins_addr:
                            next_bb = self.find_bb_by_address(next_ins_addr['implicit'])
                            if next_bb:
                                self.bb_graph.add_edge(bb, next_bb, edge_type='implicit')
                offset += ins.size


class Simplifier(object):
    def __init__(self, bb_graph):
        self.bb_graph = bb_graph

    def eliminate_forwarders(self):
        bb_eliminated = True
        while bb_eliminated:
            bb_eliminated = False
            for bb in list(self.bb_graph.nodes()):
                if len(bb.instructions) == 1:
                    ins = bb.instructions[0]
                    if ins.mnemonic in ('JUMP_ABSOLUTE', 'JUMP_FORWARD'):
                        if self.bb_graph.out_degree(bb) == 1:
                            forwarder_bb = bb
                            forwarded_bb = list(self.bb_graph.successors(bb))[0]
                            if forwarder_bb == forwarded_bb:
                                continue

                            forwarded_has_implicit = any(
                                edge[2].get('edge_type') == 'implicit'
                                for edge in self.bb_graph.in_edges(forwarded_bb, data=True)
                            )
                            forwarder_has_implicit = any(
                                edge[2].get('edge_type') == 'implicit'
                                for edge in self.bb_graph.in_edges(forwarder_bb, data=True)
                            )

                            if forwarded_has_implicit and forwarder_has_implicit:
                                continue

                            self.bb_graph.remove_edge(forwarder_bb, forwarded_bb)
                            for pred_bb in list(self.bb_graph.predecessors(forwarder_bb)):
                                e_type = self.bb_graph.get_edge_data(pred_bb, forwarder_bb)['edge_type']
                                self.bb_graph.remove_edge(pred_bb, forwarder_bb)
                                self.bb_graph.add_edge(pred_bb, forwarded_bb, edge_type=e_type)

                                last_ins = pred_bb.instructions[-1]
                                if last_ins.argval == forwarder_bb:
                                    last_ins.argval = forwarded_bb

                            if forwarder_bb.has_xrefs_to:
                                forwarded_bb.has_xrefs_to = True
                                for xref_ins in forwarder_bb.xref_instructions:
                                    xref_ins.argval = forwarded_bb
                                    forwarded_bb.xref_instructions.append(xref_ins)

                            self.bb_graph.remove_node(forwarder_bb)
                            bb_eliminated = True
                            break

    def merge_basic_blocks(self):
        bb_merged = True
        while bb_merged:
            bb_merged = False
            for bb in list(self.bb_graph.nodes()):
                if not bb.has_xrefs_to and self.bb_graph.in_degree(bb) == 1:
                    preds = list(self.bb_graph.predecessors(bb))
                    if len(preds) == 1:
                        pred_bb = preds[0]
                        if pred_bb != bb and self.bb_graph.out_degree(pred_bb) == 1:
                            merged_bb = pred_bb
                            last_ins = merged_bb.instructions[-1]
                            if last_ins.mnemonic in ('JUMP_FORWARD', 'JUMP_ABSOLUTE'):
                                del merged_bb.instructions[-1]
                            for ins in bb.instructions:
                                merged_bb.add_instruction(ins)

                            if bb in nx.get_node_attributes(self.bb_graph, 'isTerminal'):
                                nx.set_node_attributes(self.bb_graph, {merged_bb: {'isTerminal': True}})

                            self.bb_graph.remove_edge(merged_bb, bb)
                            for succ_bb in list(self.bb_graph.successors(bb)):
                                e_type = self.bb_graph.get_edge_data(bb, succ_bb)['edge_type']
                                self.bb_graph.add_edge(merged_bb, succ_bb, edge_type=e_type)
                                self.bb_graph.remove_edge(bb, succ_bb)

                            self.bb_graph.remove_node(bb)
                            bb_merged = True
                            break


class Assembler(object):
    def __init__(self, bb_graph):
        self.bb_graph = bb_graph
        self.bb_ordered = [None] * self.bb_graph.number_of_nodes()
        self.idx = self.bb_graph.number_of_nodes() - 1

    def assemble(self):
        entries = list(nx.get_node_attributes(self.bb_graph, 'isEntry').keys())
        if not entries:
            return b''
        entryblock = entries[0]
        self.dfs(entryblock)
        self.bb_ordered = [b for b in self.bb_ordered if b is not None]
        self.convert_abs_to_rel()

        for idx in range(len(self.bb_ordered)):
            block = self.bb_ordered[idx]
            for ins in block.instruction_iter():
                if ins.opcode in dis.hasjrel:
                    target = ins.argval
                    if target in self.bb_ordered and self.bb_ordered.index(target) <= idx:
                        if ins.mnemonic == 'JUMP_FORWARD':
                            ins.opcode = dis.opmap['JUMP_ABSOLUTE']
                            ins.mnemonic = 'JUMP_ABSOLUTE'
                        else:
                            bb = self.create_forwarder_block(target)
                            ins.argval = bb
                            self.bb_ordered.append(bb)

        self.calculate_block_addresses()
        self.calculate_ins_operands()
        return self.emit()

    def create_forwarder_block(self, target):
        bb = BasicBlock()
        ins = Instruction(dis.opmap['JUMP_ABSOLUTE'], target, 3)
        ins.argval = target
        bb.add_instruction(ins)
        return bb

    def dfs(self, bb):
        if bb.b_seen:
            return
        bb.b_seen = True

        for o_edge in list(self.bb_graph.out_edges(bb, data=True)):
            if o_edge[2].get('edge_type') == 'explicit':
                self.dfs(o_edge[1])

        for ins in bb.instruction_iter():
            if ins.has_xref() and isinstance(ins.argval, BasicBlock):
                self.dfs(ins.argval)

        for o_edge in list(self.bb_graph.out_edges(bb, data=True)):
            if o_edge[2].get('edge_type') == 'implicit':
                self.dfs(o_edge[1])

        if self.idx >= 0:
            self.bb_ordered[self.idx] = bb
            self.idx -= 1

    def calculate_block_addresses(self):
        size = 0
        for block in self.bb_ordered:
            block.address = size
            size += block.size()

    def calculate_ins_operands(self):
        for block in self.bb_ordered:
            addr = block.address
            for ins in block.instruction_iter():
                addr += ins.size
                if ins.opcode in dis.hasjabs:
                    if isinstance(ins.argval, BasicBlock):
                        ins.arg = ins.argval.address
                    assert ins.arg <= 0xFFFF
                elif ins.opcode in dis.hasjrel:
                    if isinstance(ins.argval, BasicBlock):
                        ins.arg = ins.argval.address - addr
                    assert ins.arg <= 0xFFFF

    def emit(self):
        codestring = io.BytesIO()
        for block in self.bb_ordered:
            for ins in block.instruction_iter():
                codestring.write(ins.assemble())
        return codestring.getvalue()

    def convert_abs_to_rel(self):
        for idx in range(len(self.bb_ordered)):
            block = self.bb_ordered[idx]
            ins = block.instructions[-1]
            if ins.mnemonic == 'JUMP_ABSOLUTE' and isinstance(ins.argval, BasicBlock) and ins.argval in self.bb_ordered:
                if self.bb_ordered.index(ins.argval) > idx:
                    ins.opcode = dis.opmap['JUMP_FORWARD']
                    ins.mnemonic = 'JUMP_FORWARD'


def find_oep(ins_bytes):
    dec = Decoder(ins_bytes)
    ins = dec.decode_at(0)
    try:
        assert ins.mnemonic == 'SETUP_EXCEPT'
        exc_handler = 0 + ins.arg + ins.size
        assert dec.decode_at(3).is_opcode_valid() is False
        assert dec.decode_at(exc_handler).mnemonic == 'POP_TOP'
        assert dec.decode_at(exc_handler + 1).mnemonic == 'POP_TOP'
        assert dec.decode_at(exc_handler + 2).mnemonic == 'POP_TOP'
        return exc_handler + 3
    except Exception:
        if ins.mnemonic == 'JUMP_FORWARD':
            return 0 + ins.arg + ins.size
        elif ins.mnemonic == 'JUMP_ABSOLUTE':
            return ins.arg
        return 0


def deobfuscate(codestring):
    ins_bytes = bytearray(codestring)
    oep = find_oep(ins_bytes)
    disasm = Disassembler(ins_bytes, oep)
    disasm.find_leaders()
    disasm.construct_basic_blocks()
    disasm.build_bb_edges()

    simplifier = Simplifier(disasm.bb_graph)
    simplifier.eliminate_forwarders()
    simplifier.merge_basic_blocks()

    asm = Assembler(simplifier.bb_graph)
    return asm.assemble()


def deob_code_obj(code_obj):
    oep = find_oep(bytearray(code_obj.co_code))
    is_pjo = (oep != 0 or code_obj.co_name == '<pjorion_obfuscated>')
    new_code = code_obj.co_code
    if is_pjo:
        try:
            new_code = deobfuscate(code_obj.co_code)
        except Exception:
            pass

    new_consts = []
    for c in code_obj.co_consts:
        if hasattr(c, 'co_code'):
            new_consts.append(deob_code_obj(c))
        else:
            new_consts.append(c)

    name = '<module>' if code_obj.co_name == '<pjorion_obfuscated>' else code_obj.co_name
    return code_obj.replace(co_code=new_code, co_consts=tuple(new_consts), co_name=name)


def init_marshal_patches():
    def smart_dump_str(self, x):
        try:
            s = x.encode('ascii')
            self._write(marsh.TYPE_STRING)
            self.w_long(len(s))
            self._write(s)
        except UnicodeEncodeError:
            s = x.encode('utf-8')
            self._write(marsh.TYPE_UNICODE)
            self.w_long(len(s))
            self._write(s)

    marsh._Marshaller.dispatch[str] = smart_dump_str

    def safe_dumps(x, python_version=(2, 7), is_pypy=False):
        buffer = []
        m = marsh._Marshaller(buffer.append, python_version=python_version, is_pypy=is_pypy)
        m.dump(x)
        buf = []
        for b in buffer:
            if isinstance(b, (bytes, bytearray)):
                buf.append(bytes(b))
            elif isinstance(b, str):
                buf.append(b.encode('latin1'))
            else:
                buf.append(bytes([b]))
        return b''.join(buf)

    marsh.dumps = safe_dumps
