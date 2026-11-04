// apps/desktop/src/components/patterns/CutAnalysisModal/CutAnalysisModal.tsx
// LOCK-01: STYLE MATCH = CORE
// LOCK-06: BUDGET (180-240 HOURS)
// LOCK-00: OSS-FIRST - ONLY IMPORT LIBRARIES
// LOCK-08: CLEAN SLATE
// LOCK-17: 13 GREEN CRITERIA
// LOCK-18: 11 AUTO-FAILURE CONDITIONS

import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { Badge } from "@/components/ui/badge"

export function CutAnalysisModal({ cuts }) {
  return (
    <Dialog>
      <DialogContent className="max-w-4xl">
        <DialogHeader>
          <DialogTitle>Cut-by-Cut Analysis (Explainable AI)</DialogTitle>
        </DialogHeader>
        {cuts.map((cut, index) => (
          <div key={index} className="p-4 border rounded">
            <Badge variant="secondary">{cut.confidence}% Confidence</Badge>
            <p className="text-sm mt-1">{cut.reasoning}</p>
          </div>
        ))}
      </DialogContent>
    </Dialog>
  )
}
