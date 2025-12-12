"""Plugin manager for dynamic module loading"""
from importlib import import_module
from logging import getLogger
from pathlib import Path
from typing import Dict, Any
from classes.input_module import InputModule
from classes.output_module import OutputModule
from classes.device_model import DeviceModel

logger = getLogger(__name__)

class PluginManager:
    """Manages plugin loading"""
    
    def __init__(self):
        self._input_cache = {}
        self._output_cache = {}
        self._model_cache = {}
    
    def load_input_module(self, module_type: str, config: Dict[str, Any]) -> InputModule:
        """Load an input module"""
        if module_type in self._input_cache:
            return self._input_cache[module_type]
        
        try:
            module = import_module(f'modules.input.{module_type}')
            class_name = ''.join(word.capitalize() for word in module_type.split('_'))
            module_class = getattr(module, class_name)
            instance = module_class(config)
            self._input_cache[module_type] = instance
            return instance
        except Exception as e:
            logger.error(f"Failed to load input module '{module_type}': {e}")
            raise
    
    def load_output_module(self, module_type: str, config: Dict[str, Any]) -> OutputModule:
        """Load an output module"""
        if module_type in self._output_cache:
            return self._output_cache[module_type]
        
        try:
            module = import_module(f'modules.output.{module_type}')
            class_name = ''.join(word.capitalize() for word in module_type.split('_'))
            module_class = getattr(module, class_name)
            instance = module_class(config)
            self._output_cache[module_type] = instance
            return instance
        except Exception as e:
            logger.error(f"Failed to load output module '{module_type}': {e}")
            raise
    
    def get_device_model(self, device_type: str) -> DeviceModel:
        """Get device model for a device type"""
        if device_type in self._model_cache:
            return self._model_cache[device_type]
        
        class_name = ''.join(word.capitalize() for word in device_type.split('_'))
        
        try:
            # Try to load module with exact device_type name
            module = import_module(f'modules.models.{device_type}')
            model_class = getattr(module, class_name)
            instance = model_class()
            self._model_cache[device_type] = instance
            return instance
        except ModuleNotFoundError:
            # Module doesn't exist, search for class in all available models
            try:
                models_dir = Path(__file__).parent.parent / 'modules' / 'models'
                for model_file in models_dir.glob('*.py'):
                    if model_file.stem.startswith('_'):
                        continue
                    try:
                        module = import_module(f'modules.models.{model_file.stem}')
                        if hasattr(module, class_name):
                            model_class = getattr(module, class_name)
                            instance = model_class()
                            self._model_cache[device_type] = instance
                            return instance
                    except:
                        continue
            except Exception as e:
                pass
        except Exception as e:
            pass
        
        # Model not found
        raise Exception(f"No model found for device type '{device_type}' (class '{class_name}')")

