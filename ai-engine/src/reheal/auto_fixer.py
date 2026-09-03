import gc
import logging
logger = logging.getLogger('reheal.fixer')

class AutoFixer:
    def auto_fix_memory(self):
        gc.collect()
        return True
