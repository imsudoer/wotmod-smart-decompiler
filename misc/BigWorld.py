
# region Unknown/TODO return types

class TODO_NATIVE_ScriptObject(object):
    pass

# endregion

# region Private native instance variables

__width = 1920
__height = 1080
__player = None

# endregion

# region Private native classes/types

class __NATIVE_Point(object):

    def __init__(self, x, y):
        self.x = x
        self.y = y

# endregion

# region Public Game classes

def __getAccountInstance():
    try:
        from Account import PlayerAccount
    except ImportError:
        return None
    return PlayerAccount()

def __getAvatarInstance():
    try:
        from Avatar import PlayerAvatar
    except ImportError:
        return None
    return PlayerAvatar()

# endregion

class AoIEntities(object):
    pass

class ArcadeAimingSystem(object):
    pass

class ArcadeAimingSystemRemote(object):
    pass

class ArenaBorderHelper(object):
    pass

class ArtyAimingSystem(object):
    pass

class ArtyAimingSystemRemote(object):
    pass

class Attachments(object):
    pass

class AutoAim(object):
    pass

class AvatarDropFilter(object):
    pass

class AvatarFilter(object):
    pass

class AvatarSubfilters(object):
    pass

class AxisEvent(object):
    pass

# class BW::DirectionCursor(object):
#     pass

class BaseCamera(object):
    pass
class BaseStrategicAimingSystem(object):
    pass

class BoidsFilter(object):
    pass

class BorderlessBehaviour(object):
    pass

class BoxAttachment(object):
    pass

class CameraSpeed(object):
    pass

class CollidableTransitionCamera(object):
    pass

class CollideSegment(object):
    pass

class CollisionAssembler(object):
    pass

class CollisionComponent(object):
    pass

class CompoundAssembler(object):
    pass

class CursorCamera(object):
    pass

class CustomRefLoader(object):
    pass

class CustomizationEnvironment(object):
    pass

class Details(object):
    pass

class DetailsVector(object):
    pass

class DiffDirProvider(object):
    pass

class DualGunAimingSystem(object):
    pass

class DualGunAimingSystemRemote(object):
    pass

class DumbFilter(object):
    pass

class DynamicScriptComponent(object):
    pass

class Entity(object):
    pass

class EntityDestroyedException(object):
    pass

class EntityDirProvider(object):
    pass

class EntityEmbodiments(object):
    pass

class EntityMProv(object):
    pass

class EnvironmentSwitcher(object):
    pass

class EventType(object):
    pass

class FailedUnpickle(object):
    pass

class FilterInterpolationType(object):
    pass

class FlexiCam(object):
    pass

class FreeCamera(object):
    pass

class GroundNormalProvider(object):
    pass

class Homer(object):
    pass

class HomingCamera(object):
    pass

class IAimingSystem(object):
    pass

class ICompoundFashion(object):
    pass

class IMEEvent(object):
    pass

class ITextureProvider(object):
    pass

class InputHandler(object):
    pass

class InvViewMatrix(object):
    pass

class KeyEvent(object):
    pass

class Latency(object):
    pass

class LatencyInfo(object):
    pass

class LinearHomer(object):
    pass

class LookupTable(object):
    pass

class MatrixProviderLiaison(object):
    pass

class Model(object):
    pass

class Motor(object):
    pass

class MouseEvent(object):
    pass

class MouseTargetingMatrix(object):
    pass

class Orbitor(object):
    pass

class Oscillator(object):
    pass

class Oscillator2(object):
    pass

class PlayerAvatarFilter(object):
    pass

class PlayerMatrix(object):
    pass

class PolygonalAreaBorder(object):
    pass

class ProjectileMotor(object):
    pass

class ProjectionAccess(object):
    pass

class Propellor(object):
    pass

class PyAttachment(object):
    pass

class PyBallisticsSimulator(object):
    pass

class PyCamoHandler(object):
    pass

class PyCollisionAssemblerProduct(object):
    pass

class PyCustomizationHelper(object):
    pass

class PyDirtHandler(object):
    pass

class PyEntities(object):
    pass

class PyEvent(object):
    pass

class PyExtrapolationData(object):
    pass

class PyFashion(object):
    pass

class PyFilter(object):
    pass

class PyGammaWizard(object):
    pass

class PyGlooxTag(object):
    pass

class PyGroundEffectManager(object):
    pass

class PyMaterialFashion(object):
    pass

class PyMaterialHandler(object):
    pass

class PyModelNode(object):
    pass

class PyOmniLight(object):
    pass

class PyOutputStream(object):
    pass

class PySalvo(object):
    pass

class PyScreener(object):
    pass

class PySplodge(object):
    pass

class PySpotLight(object):
    pass

class PyStrictPixelQuad(object):
    pass

class PyTarget(object):
    pass

class PyTerrainSelectedArea(object):
    pass

class PyTextureProvider(object):
    pass

class PyTimedWarplaneMotor(object):
    pass

class PyTrackScroll(object):
    pass

class PyTransformFashion(object):
    pass

class PyURLResponse(object):
    pass

class PyUniversalEvent(object):
    pass

class PyVOIP(object):
    pass

class PyWgArtilleryCalculator(object):
    pass

class ReplayTerminatedReason(object):
    pass

class ResourceFormat(object):
    pass

class ResourceRefs(object):
    pass

class RouteTransitionCamera(object):
    pass

class ScanDirProvider(object):
    pass

class Server(object):
    pass

class ServerCaller(object):
    pass

class ServerDiscovery(object):
    pass

class Servo(object):
    pass

class SkeletonCollider(object):
    pass

class SniperAimingSystem(object):
    pass

class SniperAimingSystemRemote(object):
    pass

class Space(object):
    pass

class SpaceIDList(object):
    pass

class SpacePtrList(object):
    pass

class SpacesMap(object):
    pass

class SpeedTreeTargetedCamera(object):
    pass

class SphericalTransitionCamera(object):
    pass

class StrategicAimingSystem(object):
    pass

class StrategicAimingSystemRemote(object):
    pass

class Targeting(object):
    pass

class ThirdPersonProvider(object):
    pass

class ThirdPersonTargetingMatrix(object):
    pass

class TrajectoryDrawer(object):
    pass

class TransformMaterialFashion(object):
    pass

class TransitionCamera(object):
    pass

class UnresolvedUDORefException(object):
    pass

class UserDataObject(object):
    pass

class WGActionCurve(object):
    pass

class WGAlphaFadeCompoundFashion(object):
    pass

class WGAlphaFadeFashion(object):
    pass

class WGBaseFashion(object):
    pass

class WGEntityFilter(object):
    pass

class WGFlagAlphaFadeFashion(object):
    pass

class WGFlockManager(object):
    pass

class WGGunRotatorImpl(object):
    pass

class WGMaterialDisabler(object):
    pass

class WGOcclusionDecal(object):
    pass

class WGPhysicalBody(object):
    pass

class WGPillboxFilter(object):
    pass

class WGPingerInstance(object):
    pass

class WGRenderSettings(object):
    pass

class WGReplayController(object):
    pass

class WGShadowForwardDecal(object):
    pass

class WGSpamFilter(object):
    pass

class WGSplineTrack(object):
    pass

class WGStickerModel(object):
    pass

class WGTankPhysics(object):
    pass

class WGTextureFashion(object):
    pass

class WGTurretFilter(object):
    pass

class WGVehicleFashion(object):
    pass

class WGVehicleFilter(object):
    pass

class WGVehiclePhysics(object):
    pass

class WGWarplaneMotor(object):
    pass

class WGWheeledPhysics(object):
    pass

class WGWinNotifier(object):
    pass

class WgVehicleOutput(object):
    pass

class XmppClient(object):
    pass

# TODO: Fix Vector2/Vector3 types
def addDecal(groupName: str, arg1: Vector3, arg2: Vector3, size: Vector2, yaw: float, texNameIdx: int, bumpTexNameIdx: int, smTextNameIdx: int) -> None:
    """Method to create decal
    arg1, arg2 are unknown
    Used in _DecalEffectDesc
    """
    pass

def addDecalGroup(name: str, lifeTime: int, trianglesCount: int) -> None:
    """Unknown method, WIP
    Used in DecalMap
    """
    pass

def addIdleCallbackForDelay(delay: float, startCallback: function, stopCallback: function) -> None:
    """Add idle callback with delay
    Used in HangarCameraIdle"""
    pass

def addMarkEnterToRegion(name: str) -> None:
    """Unknown method, WIP
    Probably used for uniprof regions"""
    pass

def addMarkExitFromRegion(name: str) -> None:
    """Unknown method, WIP
    Probably used for uniprof regions"""
    pass

def addModel(model: Model, spaceID: int = 0) -> None:
    """Create BigWorld.Model instance"""
    pass

def addSpaceGeometryMapping(spaceID, mapper, path: str, visMask: int = -1) -> int:
    """Create mapping for spaceID on path
    Used in game codebase"""
    pass

def addTextureFeed(path: str, provider: PyTextureProvider) -> None:
    """Unknown method, WIP
    Not used in codebase"""
    pass

def addUPLMessage(stateName: str) -> None:
    """Dumps somewhere stateName internally?
    Used in game codebase in StatisticsCollector.noteHangarLoadingState"""
    pass

# TODO: Clarify args/kwargs if possible and return type
def addWatcher(name: str, getter: function, setter: function, description: str, *args, **kwargs) -> TODO_NATIVE_ScriptObject:
    """Adds watcher, behaviour is unknown
    Used in FovExtended/_TrajectoryDrawerImpl"""
    pass

def allEntities() -> PyEntities:
    """Deprecated alias of BigWorld.entities, see bwdeprecations"""
    pass

def appendCameraCollider(colliderData: tuple) -> None:
    """Unknown method, receives tuple of (colliderID, (partsIdxs, ))
    Used in CompoundAppearance and HangarVehicleAppearance"""
    pass

def applyGraphicPreset(preset: tuple) -> bool:
    """Apply graphic preset from a tuple
    Not present in py codebase"""
    pass

def autoDetectGraphicsSettings() -> int:
    """Get preset index after internally testing user's hardware
    Used in SettingsWindow"""
    pass

def axisDirection(arg0: int) -> int:
    """Unknown method, WIP
    Not used in py codebase"""
    pass

def buildBlueprint():
    pass

def cachedEntities():
    pass

def callback():
    pass

def camera():
    pass

def cameraSpaceID():
    pass

def cameraSpeed():
    pass

def canToDowngradePreset():
    pass

def cancelCallback():
    pass

def changeFullScreenAspectRatio():
    pass

def changeVideoMode():
    pass

def checkAndRecalculateIfPositionInExtremeProjection():
    pass

def checkUnattended():
    pass

def clearAllSpaces():
    pass

def clearBlueprint():
    pass

def clearEntitiesAndSpaces():
    pass

def clearSpace():
    pass

def clearTextureReuseList():
    pass

def clearTextureStreamingViewpoints():
    pass

def collectLastMemoryCriticalEvent():
    pass

def collectMemoryUsage():
    pass

def collide():
    pass

def commandLineLogin():
    pass

def commitPendingGraphicsSettings():
    pass

def component():
    pass

def connect():
    pass

def connectedEntity():
    pass

def consumerBuild():
    pass

def controlEntity():
    pass

def controlPointSetHeight():
    pass

def createBrowser():
    pass

def createEntity():
    pass

def createPlayerEntity():
    pass

def createSpace():
    pass

def createWebView():
    pass

def criticalExit():
    pass

def currentGraphicPresetKey():
    pass

def dcursor():
    pass

def debugDropFilter():
    pass

def debugModel():
    pass

def debugNearPlane():
    pass

def delModel():
    pass

def delSpaceGeometryMapping():
    pass

def delTextureFeed():
    pass

def delWatcher():
    pass

def delaySpaceLoad():
    pass

def destroyBrowser():
    pass

def destroyEntity():
    pass

def destroyWebView():
    pass

def detectGraphicsPresetFromSystemSettings():
    pass

def digest():
    pass

def disconnect():
    pass

def enableBattleStatisticCollector():
    pass

def enableBlueprintBuilding():
    pass

def enableDRRAutoscaling():
    pass

def enableEdgeDrawerVisual():
    pass

def enableFreeCameraModeForShadowManager():
    pass

def enableLoadingTimer():
    pass

def enterSpace():
    pass

def entities():
    pass

def entity():
    pass

def exit():
    pass

def fetchURL():
    pass

def finishDelayedLoading():
    pass

def flushPythonLog():
    pass

def generateGfxSettings():
    pass

def getActiveMonitorIndex():
    pass

def getAspectRatio():
    pass

def getAutoDetectGraphicsSettingsScore():
    pass

def getBattleFPS():
    pass

def getBorderlessParameters():
    pass

def getColorBCSSetup():
    pass

def getColorBrightness():
    pass

def getColorContrast():
    pass

def getColorGradingStrength():
    pass

def getColorSaturation():
    pass

def getDRRAutoscalerBaseScale():
    pass

def getDRRScale():
    pass

def getExclusiveFullscreenMonitorIndex():
    pass

def getExtensionsDirList():
    pass

def getFPS():
    pass

def getFileMappingMemory():
    pass

def getFullScreenAspectRatio():
    pass

def getGammaCorrection():
    pass

def getGenericMemory():
    pass

def getGraphicsPreset():
    pass

def getGraphicsPresetPropertyNames():
    pass

def getGraphicsPresets():
    pass

def getGraphicsPresetsIndices():
    pass

def getGraphicsSetting():
    pass

def getGraphicsSettingApplyMethod():
    pass

def getHeapMemory():
    pass

def getImageMemory():
    pass

def getIsImpassableZoneEnabled():
    pass

def getMaterialKinds():
    pass

def getMemoryInfoKB():
    pass

def getScaleformMemory():
    pass

def getStreamingMemory():
    pass

def getSurfMemory():
    pass

def getSystemPerformancePresetIdFromName():
    pass

def getTextureFeed():
    pass

def getUniProfMemory():
    pass

def getWWiseMemory():
    pass

def getWatcher():
    pass

def getWatcherDir():
    pass

def getWin32HeapMemory():
    pass

def getWindowMode():
    pass

def graphicSetting():
    pass

def graphicSettingIsSupported():
    pass

def graphicsSettings():
    pass

def graphicsSettingsNeedRestart():
    pass

def graphicsSettingsStatus():
    pass

def hangarDestroyed():
    pass

def hangarLoaded():
    pass

def hasPendingGraphicsSettings():
    pass

def importantGraphicSettings():
    pass

def isApplyHighQualityPossible():
    pass

def isArrayDictDataInstance():
    pass

def isClientSpace():
    pass

def isCustomGraphicPreset():
    pass

def isDRRAutoscalingEnabled():
    pass

def isDRRAutoscalingPaused():
    pass

def isDynamicDecalEnabled():
    pass

def isEval():
    pass

def isFixedDictDataInstance():
    pass

def isForwardPipeline():
    pass

def isKeyDown():
    pass

def isNextTickPending():
    pass

def isSSAOEnabled():
    pass

def isShadowsEnabled():
    pass

def isTesselationSupported():
    pass

def isTripleBuffered():
    pass

def isVideoVSync():
    pass

def isWindowVisible():
    pass

def keyToString():
    pass

def leaveSpace():
    pass

def listBorderlessResolutionsAllMonitors():
    pass

def listVideoModes():
    pass

def listVideoModesAllMonitors():
    pass

def loadResourceListBG():
    pass

def loadResourceListFG():
    pass

def lobbyStarted():
    pass

def locale():
    pass

def logCritical():
    pass

def logDebug():
    pass

def logError():
    pass

def logExceptionFrame():
    pass

def logExceptionTraceback():
    pass

def logHack():
    pass

def log():
    pass

def logNotice():
    pass

def logTrace():
    pass

def logWarning():
    pass

def loginEntered():
    pass

def makeScreenshotMarkInReplay():
    pass

def makeWorldMatrix():
    pass

def mapVirtualKey():
    pass

def markerHelperScale():
    pass

def memUsed():
    pass

def memoryDebug():
    pass

def models():
    pass

def notify():
    pass

def notifyBattleTime():
    pass

def notifySpaceChange():
    pass

def objectLod():
    pass

def onInterfaceScaleChanged():
    pass

def overloadBorders():
    pass

def overrideGraphicsSetting():
    pass

def pauseDRRAutoscaling():
    pass

def platform():
    pass

def playMovie():
    pass

def player():
    return __player

# Make IDE think that it can be either Account or Avatar type
__player = __getAccountInstance()
__player = __getAvatarInstance()

def playerDead():
    pass

def printMainLoopTasksOrder():
    pass

def probe():
    pass

def projection():
    pass

def protocolVersion():
    pass

def purgeUrlRequestCache():
    pass

def quit():
    pass

def registerShadowCaster():
    pass

def registerTextureStreamingViewpoint():
    pass

def reinitLoggers():
    pass

def reinitVideoSound():
    pass

def releaseSpace():
    pass

def removeAllIdleCallbacks():
    pass

def removeCameraCollider():
    pass

def resetEntityManager():
    pass

def resetGraphicsSettingsStatus():
    pass

def resetPlayerTargetFrom():
    pass

def resetSettingsUsingDefault():
    pass

def resizeWindow():
    pass

def restartGame():
    pass

def saveAllocationStatsToFile():
    pass

def saveAllocationsToCacheGrindFile():
    pass

def saveAllocationsToFile():
    pass

def saveMemoryUsagePerTexture():
    pass

def savePreferences():
    pass

def screenHeight():
    pass

def screenShot():
    pass

def screenSize():
    pass

def screenWidth():
    pass

def server():
    pass

def serverDiscovery():
    pass

def serverTime():
    pass

def setActiveMonitorIndex():
    pass

def setBorderlessFixedSize():
    pass

def setBorderlessFullscreen():
    pass

def setBorderlessParametersDirect():
    pass

def setBorderlessUnconstrained():
    pass

def setBorderlessWorkAreaMaximized():
    pass

def setColorBCSSetup():
    pass

def setColorBrightness():
    pass

def setColorContrast():
    pass

def setColorGradingStrength():
    pass

def setColorSaturation():
    pass

def setCursor():
    pass

def setDRRScale():
    pass

def setDamageStickerCriticalAngle():
    pass

def setEdgeDrawerImpenetratableZoneOverlay():
    pass

def setEdgeDrawerPenetratableZoneOverlay():
    pass

def setEdgeDrawerRenderMode():
    pass

def setFinalFlushURLRequestsTimeout():
    pass

def setGammaCorrection():
    pass

def setGraphicPresetByIndex():
    pass

def setGraphicPresetByName():
    pass

def setGraphicsSetting():
    pass

def setIsImpassableZoneEnabled():
    pass

def setMinLodBiasForTanks():
    pass

def setPlayerTargetTo():
    pass

def setSpeedTreeCollisionBody():
    pass

def setTextureMinMip():
    pass

def setTextureStreamingMode():
    pass

def setTripleBuffering():
    pass

def setVideoVSync():
    pass

def setWatcher():
    pass

def sinkKeyEvents():
    pass

def solvePow():
    pass

def spaceLoadStatus():
    pass

def spaceTimeOfDay():
    pass

def spaces():
    pass

def startBenchmarkTool():
    pass

def statLagDetected():
    pass

def statPing():
    pass

def stime():
    pass

def stopBenchmarkTool():
    pass

def stopLoadResourceListBGTask():
    pass

def stringToKey():
    pass

def target():
    pass

def targeting():
    pass

def time():
    pass

def timeExact():
    pass

def timeOfDay():
    pass

def trackPhysicsQuality():
    pass

def uniprofRegionEnter():
    pass

def uniprofRegionExit():
    pass

def uniprofSceneStart():
    pass

def unregisterShadowCaster():
    pass

def updateCurrentPresetIndex():
    pass

def updateTerrainBorders():
    pass

def videoModeIndex():
    pass

def virtualTextureRenderComplete():
    pass

# region WG-added methods

def WG_dirtEnabled() -> bool:
    pass

def wgAddEdgeDetectCompoundModel():
    pass

def wgAddEdgeDetectDynamicModel():
    pass

def wgAddEdgeDetectEntity():
    pass

def wgAddIgnoredCollisionEntity():
    pass

def wgDelEdgeDetectCompoundModel():
    pass

def wgDelEdgeDetectDynamicModel():
    pass

def wgDelEdgeDetectEntity():
    pass

def wgDelIgnoredCollisionEntity():
    pass

def wgGetBenchmarkLocations():
    pass

def wgSetEdgeDetectEdgeColor():
    pass

def wgSetEdgeDetectPatternColors():
    pass

def wgSetEdgeDetectSolidColors():
    pass

def wg_addDecal():
    pass

def wg_addDecalGroup():
    pass

def wg_addMatkindScaleU():
    pass

def wg_addScaleformTexture():
    pass

def wg_addTempScaleformTexture():
    pass

def wg_addWaterRipples():
    pass

def wg_alloc():
    pass

def wg_applyOverlayToModel():
    pass

def wg_binoculars():
    pass

def wg_bringWindowToForeground():
    pass

def wg_calcGunPitchLimits():
    pass

def wg_changeStringCasing():
    pass

def wg_checkAnyParticlesExist():
    pass

def wg_checkDestructibleIsBush():
    pass

def wg_clearAllScaleformTextures():
    pass

def wg_clearCrashedState():
    pass

def wg_clearDecals():
    pass

def wg_clearTextureReuseList():
    pass

def wg_collectScaleformTextures():
    pass

def wg_collideDynamic():
    pass

def wg_collideDynamicStatic():
    pass

def wg_collideDynamics():
    pass

def wg_collideSegment():
    pass

def wg_collideWater():
    pass

def wg_computeProjectileTrajectory():
    pass

def wg_copyToClipboard():
    pass

def wg_cpdata(data: str) -> str:
    """Write crypted data
    Used in codebase (login/preferences).
    """
    pass

def wg_cpsalt():
    pass

def wg_crash():
    pass

def wg_createSplineTrack():
    pass

def wg_debugLogging():
    pass

def wg_decalTextureIndex():
    pass

def wg_defaultFlagEmblemCoords():
    pass

def wg_defaultFlagEmblemPath():
    pass

def wg_destroyFallAtom():
    pass

def wg_destroyFragile():
    pass

def wg_destroyModule():
    pass

# Disable lobby FPS limiter
def wg_disableSpecialFPSMode():
    pass

def wg_dumpScaleformMemoryReport():
    pass

def wg_enableGUIBackground():
    pass

def wg_enableInputEvents():
    pass

def wg_enableKeyboardEvents():
    pass

def wg_enableMouseEvents():
    pass

def wg_enableTreeHiding():
    pass

def wg_eraseScaleformResFromCache():
    pass

def wg_eraseScaleformTexture():
    pass

def wg_firstDayOfWeek():
    pass

def wg_free():
    pass

def wg_getCappedShotTargetInfos():
    pass

def wg_getChunkDestrFilenames():
    pass

def wg_getChunkMatrix():
    pass

def wg_getChunkModelFashion():
    pass

def wg_getClientStatistics():
    pass

def wg_getCurrentResolution():
    pass

def wg_getDestructibleEffectCategory():
    pass

def wg_getDestructibleEffectName():
    pass

def wg_getDestructibleEffectScale():
    pass

def wg_getDestructibleEffectsTintColor():
    pass

def wg_getDestructibleFallPitchConstr():
    pass

def wg_getDestructibleFilename():
    pass

def wg_getDestructibleHeight():
    pass

def wg_getDestructibleLifetimeEffectChance():
    pass

def wg_getDestructibleMatrix():
    pass

def wg_getFallingParams():
    pass

def wg_getFrameTimestamp():
    pass

def wg_getHangarStatistics():
    pass

def wg_getHardPointMatrix():
    pass

def wg_getLangCode():
    pass

def wg_getMatInfoNearPoint():
    pass

def wg_getMathInfoUnderPoint():
    pass

def wg_getMaxBorderlessResolution():
    pass

def wg_getMaxWindowedResolution():
    pass

def wg_getMonitorNames():
    pass

def wg_getNMHardPointMatrix():
    pass

def wg_getNativeScreenResoulution():
    pass

def wg_getPreferencesFilePath():
    pass

def wg_getProductVersion():
    pass

def wg_getShotAngles():
    pass

def wg_getShotAnglesNew():
    pass

def wg_getSpaceBounds():
    pass

def wg_getSpaceItemsVisibilityMask():
    pass

def wg_getTimePerFrame():
    pass

def wg_havokExplosion():
    pass

def wg_havokSetSniperMode():
    pass

def wg_havokWipe():
    pass

def wg_initCustomSettings():
    pass

def wg_isCapsLockOn():
    pass

def wg_isDestrCanBeActivated():
    pass

def wg_isHavokActive():
    pass

def wg_isNumLockOn():
    pass

def wg_isSSE2Supported():
    pass

def wg_isScrollLockOn():
    pass

def wg_isSniperModeSwingingEnabled():
    pass

def wg_isVehicleDustEnabled() -> bool:
    """ Determine whether user enabled dust effects for vehicle
    :returns bool
    """
    pass

def wg_openWebBrowser():
    pass

def wg_precacheScaleformResource():
    pass

def wg_preferencesExistedAtStartup():
    pass

def wg_prefetchSpaceZip():
    pass

def wg_printScaleformCacheStatictics():
    pass

def wg_quitAndStartLauncher():
    pass

def wg_registerDamageSticker():
    pass

def wg_reportSessionData():
    pass

def wg_reportSystemData():
    pass

def wg_resolveFileName():
    pass

def wg_restoreDestructibles():
    pass

def wg_saveWatchers():
    pass

def wg_setAdapterOrdinalNotifyCallback():
    pass

def wg_setAimingParam():
    pass

def wg_setChunkModelFashion():
    pass

def wg_setDestructibleActive():
    pass

def wg_setDestructibleMatrix():
    pass

def wg_setFlagColor():
    pass

def wg_setFlagEmblem():
    pass

def wg_setGUIBackground():
    pass

def wg_setHourOfDay():
    pass

def wg_setMaxFrameRate():
    pass

def wg_setObservableMProv():
    pass

def wg_setPyModelTexture():
    pass

def wg_setRedefineKeysMode():
    pass

def wg_setReducedFpsMode():
    pass

def wg_setScreenshotNotifyCallback():
    pass

def wg_setSpaceItemsVisibilityMask():
    pass

# Enable lobby FPS limiter
def wg_setSpecialFPSMode():
    pass

def wg_setTreeHidingRadius():
    pass

def wg_setWaterFreqX():
    pass

def wg_setWaterFreqZ():
    pass

def wg_setWaterTexScale():
    pass

def wg_setupGroundMaterialsMap():
    pass

def wg_setupMaterialHardness():
    pass

def wg_setupPhysicsParam():
    pass

def wg_simulateProjectileTrajectory(beginPoint: tuple, velocity: tuple, gravity: tuple, time: float, epsilon: float, skipFlags: int = 128, requiredFlags: int = 0):
    """Unknown method, WIP
    Not used in codebase
    """
    pass

def wg_solveDestructibleFallPitch(weight: float, angStiffness: float, unknown0: float, approxPitch: float) -> float:
    """Unknown method, WIP
    Used in _DestructiblesAnimator.
    unknown0 -> pitchConstr - springAngle
    """
    pass

def wg_subscribeToReadPreferences(callback: function) -> None:
    """Events that fired on preferences read to tweak them
    Used in account_helpers.settings_core.options.PreferencesSetting"""
    pass

def wg_subscribeToSavePreferences(callback: function) -> None:
    """Events that fired on preferences write to tweak them
    Used in account_helpers.settings_core.options.PreferencesSetting"""
    pass

def wg_traceTextureIndex(textName: str) -> int:
    """Unknown method, WIP.
    Used in DecalMap._readCfg"""
    pass

# TODO: fill return type
def wg_trajectory_drawer() -> ClassType:
    """Get TrajectoryDrawer that used in Arty/Strategic mode."""
    pass

def wg_translateToScaleformKeyCode(keycode: int) -> int:
    """Transform Keys.KEY_* to Scaleform key code?
    Unknown method, WIP
    Not used in codebase
    """
    pass

def wg_ucpdata(src: str) -> str:
    """Read crypted data?
    Used in codebase (login/preferences).
    """
    pass

def wg_unsubAllSavePreferences():
    """Unknown method, WIP."""
    pass

def wg_updateColorGrading() -> None:
    """Unknown method, WIP.
    Triggered in ArenaLoadController.startControl"""
    pass

def wg_writeToStdOut(text: str) -> None:
    """Used to write to stdout in `game.start` when ScriptedTest failed to start."""
    pass

# endregion

def windowSize() -> __NATIVE_Point:
    """Get window size"""
    return __NATIVE_Point(__width, __height)

def worldDrawEnabled(newDrawEnabled: bool | None = None) -> None:
    """Get window size"""
    pass
