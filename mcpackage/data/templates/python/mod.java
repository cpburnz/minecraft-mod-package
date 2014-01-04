package ${mod_package};

import cpburnz.minecraft.pymod.JavaMod;
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
public final class ${mod_class}(JavaMod) {

	/**
	 * The singleton instance of this mod for Forge.
	 */
	@Instance("${mod_id}")
	public static ${mod_class} instance;

	/**
	 * Send the pre-initialization event to the python mod.
	 *
	 * *event* is the pre-initialization event.
	 */
	@EventHandler
	public void preInit(FMLPreInitializationEvent event) {
		super.preInit(event);
	}

	/**
	 * Send the initialization event to the python mod.
	 *
	 * *event* is the initialization event.
	 */
	@EventHandler
	public void init(FMLInitializationEvent event) {
		super.init(event);
	}

	/**
	 * Send the inter-mod communications event to the python mod.
	 *
	 * *event* is the inter-mod communications event.
	 */
	@EventHandler
	public void interModComms(FMLInterModComms event) {
		super.interModComms(event);
	}

	/**
	 * Send the post-initialization event to the python mod.
	 *
	 * *event* is the post-initialization event.
	 */
	@EventHandler
	public void postInit(FMLPostInitializationEvent event) {
		super.postInit(event);
	}

	/**
	 * Send the server-about-to-start event to the python mod.
	 *
	 * *event* is the server-about-to-start event.
	 */
	@EventHandler
	public void serverAboutToStart(FMLServerAboutToStartEvent event) {
		super.serverAboutToStart(event);
	}

	/**
	 * Send the server-starting event to the python mod.
	 *
	 * *event* is the server-starting event.
	 */
	@EventHandler
	public void serverStarting(FMLServerStartingEvent event) {
		super.serverStarting(event);
	}

	/**
	 * Send the server-started event to the python mod.
	 *
	 * *event* is the server-started event.
	 */
	@EventHandler
	public void serverStarted(FMLServerStartedEvent event) {
		super.serverStarted(event);
	}

	/**
	 * Send the server-stopping event to the python mod.
	 *
	 * *event* is the server-stopping event.
	 */
	@EventHandler
	public void serverStopping(FMLServerStoppingEvent event) {
		super.serverStopping(event);
	}

	/**
	 * Send the server-stopped event to the python mod.
	 *
	 * *event* is the server-stopped event.
	 */
	@EventHandler
	public void serverStopped(FMLServerStoppedEvent event) {
		super.serverStopped(event);
	}

}
