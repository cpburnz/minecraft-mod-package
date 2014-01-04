package ${mod_package};

import java.util.logging.Level;

import cpw.mods.fml.common.FMLLog;
import cpw.mods.fml.common.Mod;
import cpw.mods.fml.common.Mod.EventHandler;
import cpw.mods.fml.common.event.FMLInitializationEvent;
import cpw.mods.fml.common.event.FMLInterModComms;
import cpw.mods.fml.common.event.FMLPostInitializationEvent;
import cpw.mods.fml.common.event.FMLPreInitializationEvent;
import cpw.mods.fml.common.event.FMLServerAboutToStartEvent;
import cpw.mods.fml.common.event.FMLServerStartedEvent;
import cpw.mods.fml.common.event.FMLServerStartingEvent;
import cpw.mods.fml.common.event.FMLServerStoppedEvent;
import cpw.mods.fml.common.event.FMLServerStoppingEvent;

/**
 * ${mod_name}.
 */
@Mod(modid="${mod_id}". useMetadata=true)
public final class ${mod_class} {

	/**
	 * The singleton instance of this mod for Forge.
	 */
	@Instance("${mod_id}")
	public static ${mod_class} instance;

	/**
	 * The name to use when logging.
	 */
	private String logName;

	/**
	 * Initializes the instance.
	 */
	public ${mod_class}() {
		// Get mod ID.
		final Mod modInfo = this.getClass().getAnnotation(Mod.class);
		this.logName = modInfo.modid();
	}

	/**
	 * Called when the pre-initialization event occurs. This is run before
	 * anything else. Read your config, create blocks, items, etc., and register
	 * them with the ``GameRegistery``.
	 *
	 * *event* is the pre-initialization event.
	 */
	@EventHandler
	public void preInit(FMLPreInitializationEvent event) {
		FMLLog.log(this.logName, Level.FINE, "Pre-initialization.");
	}

	/**
	 * Called when the initialization event occurs. Do your mod setup. Build
	 * whatever data structures you care about. Register recipes, send inter-mod
	 * communication messages to other mods.
	 *
	 * *event* is the initialization event.
	 */
	@EventHandler
	public void init(FMLInitializationEvent event) {
		FMLLog.log(this.logName, Level.FINE, "Initialization.");
	}

	/**
	 * Called when the inter-mod communications event occurs.
	 *
	 * *event* is the inter-mod communications event.
	 */
	@EventHandler
	public void interModComms(FMLInterModComms event) {
		FMLLog.log(this.logName, Level.FINE, "Inter-mod communications.");
	}

	/**
	 * Called when the post-initialization event occurs. Handle interaction with
	 * other mods, complete your setup based on this.
	 *
	 * *event* is the post-initialization event.
	 */
	@EventHandler
	public void postInit(FMLPostInitializationEvent event) {
		FMLLog.log(this.logName, Level.FINE, "Post-initialization.");
	}

	/**
	 * Called when the server-about-to-start event occurs. Use if you need to
	 * handle something before the server has even been created.
	 *
	 * *event* is the server-about-to-start event.
	 */
	@EventHandler
	public void serverAboutToStart(FMLServerAboutToStartEvent event) {
		FMLLog.log(this.logName, Level.FINE, "Server-about-to-start.");
	}

	/**
	 * Called when the server-starting event occurs. Do you stuff you need to do
	 * to setup the server. Register commands, treak the server.
	 *
	 * *event* is the server-starting event.
	 */
	@EventHandler
	public void serverStarting(FMLServerStartingEvent event) {
		FMLLog.log(this.logName, Level.FINE, "Server-starting.");
	}

	/**
	 * Called when the server-started event occurs. Do what you need to with the
	 * running server.
	 *
	 * *event* is the server-started event.
	 */
	@EventHandler
	public void serverStarted(FMLServerStartedEvent event) {
		FMLLog.log(this.logName, Level.FINE, "Server-started.");
	}

	/**
	 * Called when the server-stopping event occurs. Do what you need to do
	 * before the server has started its shutdown sequence.
	 *
	 * *event* is the server-stopping event.
	 */
	@EventHandler
	public void serverStopping(FMLServerStoppingEvent event) {
		FMLLog.log(this.logName, Level.FINE, "Server-stopping.");
	}

	/**
	 * Called when the server-stopped event occurs. Do whatever clean-up you
	 * need once the server has shutdown. Generally only useful on the
	 * integrated server.
	 *
	 * *event* is the server-stopped event.
	 */
	@EventHandler
	public void serverStopped(FMLServerStoppedEvent event) {
		FMLLog.log(this.logName, Level.FINE, "Server-stopped.");
	}

}
