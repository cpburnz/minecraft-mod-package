package ${mod_package};

import cpburnz.minecraft.java.IPyMod;
import cpburnz.minecraft.java.PyModMod;
import cpw.mods.fml.common.FMLLog;
import cpw.mods.fml.common.Mod;
import cpw.mods.fml.common.event.FMLInitializationEvent;
import cpw.mods.fml.common.event.FMLInterModComms;
import cpw.mods.fml.common.event.FMLPostInitializationEvent;
import cpw.mods.fml.common.event.FMLPreInitializationEvent;
import cpw.mods.fml.common.event.FMLServerAboutToStartEvent;
import cpw.mods.fml.common.event.FMLServerStartedEvent;
import cpw.mods.fml.common.event.FMLServerStartingEvent;
import cpw.mods.fml.common.event.FMLServerStoppedEvent;
import cpw.mods.fml.common.event.FMLServerStoppingEvent;

@Mod(modid="${mod_id}". useMetadata=true)
public abstract class ${mod_class} {

	// The singleton instance of this mod for Forge.
	@Instance("${mod_id}")
	public static ${mod_class} instance;

	// The wrapped python mod instance.
	private IPyMod pymod;

	public ${mod_class}() {

	}

	// Default is "{package}.python" where "{package}" is the package of the
	// java class
	public String getPythonModuleName() {
		return this.getClass().getPackage().getName() + ".python";
	}

	// Default is the same name as the java class.
	public String getPythonClassName() {
		return this.getClass().getSimpleName();
	}

	public void preInit(FMLPreInitializationEvent event) {
		// Get mod ID.
		Mod modInfo = this.getClass().getAnnotation(Mod.class);
		this.logName = modInfo.modid();

		// Instantiate mod class.
		final String moduleName = this.getPythonModuleName();
		final String className = this.getPythonClassName();
		this.log(Level.INFO, "Load %s.%s", moduleName, className);
		this.pymod = (IPyMod)PyModMod.jython.callClass(moduleName, className).__tojava__(IPyMod.class);
		this.log(Level.INFO, "Instance " + this.pymod);

		// Call mod pre-init.
		this.log(Level.INFO, "Pre-initialization.");
		this.pymod.preInit(event);
	}

	public void init(FMLInitializationEvent event) {
		this.log(Level.INFO, "Initialization.");
		this.pymod.init(event);
	}

	public void interModComms(FMLInterModComms event) {
		this.log(Level.INFO, "Inter mod communications.");
		this.pymod.interModComms(event);
	}

	public void postInit(FMLPostInitializationEvent event) {
		this.log(Level.INFO, "Post-initialization.");
		this.pymod.postInit(event);
	}

	public void serverAboutToStart(FMLServerAboutToStartEvent event) {
		this.log(Level.INFO, "Server about to start.");
		this.pymod.serverAboutToStart(event);
	}

	public void serverStarting(FMLServerStartingEvent event) {
		this.log(Level.INFO, "Server starting.");
		this.pymod.serverStarting(event);
	}

	public void serverStarted(FMLServerStartedEvent event) {
		this.log(Level.INFO, "Server started.");
		this.pymod.serverStarted(event);
	}

	public void serverStopping(FMLServerStoppingEvent event) {
		this.log(Level.INFO, "Server stopping.");
		this.pymod.serverStopping(event);
	}

	public void serverStopped(FMLServerStoppedEvent event) {
		this.log(Level.INFO, "Server stopped.");
		this.pymod.serverStopped(event);
	}

}
