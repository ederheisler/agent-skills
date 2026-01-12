"""Plugin installation and management"""
import logging
import shutil
from pathlib import Path
from typing import List

from .models import SkillInfo
from .utils import load_frontmatter

logger = logging.getLogger(__name__)


def load_plugins() -> List[SkillInfo]:
    """List all available plugins from plugins directory"""
    plugins = []
    # Assumes plugins are in project_root/plugins
    plugins_dir = Path(__file__).parent.parent / "plugins"

    if plugins_dir.exists():
        for p_dir in sorted(plugins_dir.iterdir()):
            if p_dir.is_dir() and (p_dir / "plugin").exists():
                readme = p_dir / "README.md"
                # Fallback to dir name if README doesn't exist or is empty
                name_from_fm, description = load_frontmatter(readme)
                name = name_from_fm or p_dir.name
                
                plugins.append(SkillInfo(
                    name=name,
                    description=description,
                    path=p_dir,
                    dir_name=p_dir.name,
                    type="plugin"
                ))
    return plugins


def remove_plugin(plugin: SkillInfo) -> None:
    """Remove a plugin"""
    # We need to find the main js file.
    src_plugin_dir = plugin.path / "plugin"
    main_js_files = list(src_plugin_dir.glob("*.js"))
    if not main_js_files:
        logger.warning(f"No JS file found in {src_plugin_dir}")
        return
        
    plugin_name = main_js_files[0].name # e.g. superpowers.js

    # Symlink location
    plugin_target = Path.home() / ".config" / "opencode" / "plugin" / plugin_name
    if plugin_target.exists():
        plugin_target.unlink()
        logger.info(f"✓ Removed plugin symlink: {plugin_target}")

    # User copy location
    user_superpowers = Path.home() / ".config" / "opencode" / "superpowers"
    user_plugin_path = user_superpowers / ".opencode" / "plugin" / plugin_name
    
    if user_plugin_path.exists():
        user_plugin_path.unlink()
        logger.info(f"✓ Removed copied plugin: {user_plugin_path}")
        
    # Remove lib files if any
    src_lib_dir = plugin.path / "lib"
    if src_lib_dir.exists():
        for lib_file in src_lib_dir.glob("*"):
            user_lib_path = user_superpowers / "lib" / lib_file.name
            if user_lib_path.exists():
                user_lib_path.unlink()
                logger.info(f"✓ Removed copied lib: {user_lib_path}")


def install_plugin(plugin: SkillInfo) -> None:
    """Install a plugin"""
    plugin_dir = Path.home() / ".config" / "opencode" / "plugin"
    plugin_dir.mkdir(parents=True, exist_ok=True)

    src_plugin_dir = plugin.path / "plugin"
    main_js_files = list(src_plugin_dir.glob("*.js"))
    if not main_js_files:
        raise FileNotFoundError(f"No JS file found in {src_plugin_dir}")
    
    main_js_file = main_js_files[0]
    plugin_name = main_js_file.name

    user_superpowers = Path.home() / ".config" / "opencode" / "superpowers"
    user_plugin_dir = user_superpowers / ".opencode" / "plugin"
    user_lib_dir = user_superpowers / "lib"
    user_plugin_dir.mkdir(parents=True, exist_ok=True)
    user_lib_dir.mkdir(parents=True, exist_ok=True)

    user_plugin_path = user_plugin_dir / plugin_name
    shutil.copy2(main_js_file, user_plugin_path)
    logger.info(f"✓ Copied plugin to {user_plugin_path}")

    # Copy libs
    src_lib_dir = plugin.path / "lib"
    if src_lib_dir.exists():
        for lib_file in src_lib_dir.glob("*"):
            user_lib_path = user_lib_dir / lib_file.name
            shutil.copy2(lib_file, user_lib_path)
            logger.info(f"✓ Copied lib {lib_file.name} to {user_lib_path}")

    # Symlink
    target = plugin_dir / plugin_name
    if target.exists() or target.is_symlink():
        target.unlink()
    target.symlink_to(user_plugin_path)
    logger.info(f"✓ Installed plugin symlink: {target} -> {user_plugin_path}")


def get_installed_plugins() -> List[str]:
    """Get list of installed plugin names (based on symlinks in config dir)"""
    installed = []
    plugin_dir = Path.home() / ".config" / "opencode" / "plugin"
    if plugin_dir.exists():
        for item in plugin_dir.iterdir():
            # If it's a symlink or file, we count it. 
            # We compare against the 'dir_name' of the skill? 
            # No, 'dir_name' of the skill is the folder name in repo (e.g. 'superpowers').
            # The plugin name is 'superpowers.js'.
            # This mismatch is annoying.
            # load_plugins uses 'p_dir.name' as 'dir_name'.
            # load_plugins uses 'name' from frontmatter or 'p_dir.name'.
            
            # Helper: We need to map installed .js files back to plugin directory names if possible,
            # or just assume the plugin directory name matches the js file name without .js?
            # In 'superpowers' folder, the js file is 'plugin/superpowers.js'.
            # So if we see 'superpowers.js' in config dir, it corresponds to 'superpowers' skill.
            
            # Let's assume the plugin dir name is the stem of the js file?
            if item.suffix == ".js":
                installed.append(item.stem) # 'superpowers'
                
    return installed
