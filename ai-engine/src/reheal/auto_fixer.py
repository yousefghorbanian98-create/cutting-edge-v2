"""Reheal Loop — Auto Fixer"""
import gc, logging
logger = logging.getLogger("reheal.fixer")

class AutoFixer:
    def fix_memory(self):
        logger.info("Auto-fixing RAM...")
        gc.collect()
        try:
            import torch
            if torch.cuda.is_available(): torch.cuda.empty_cache()
        except ImportError: pass
        try:
            import cv2; cv2.destroyAllWindows()
        except: pass
        return True

    def fix_gpu(self):
        logger.info("Auto-fixing GPU...")
        try:
            import torch
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
                torch.cuda.synchronize()
        except ImportError: pass
        return True

    def fix(self, component: str) -> bool:
        if component == "RAM": return self.fix_memory()
        if component == "GPU": return self.fix_gpu()
        return False
