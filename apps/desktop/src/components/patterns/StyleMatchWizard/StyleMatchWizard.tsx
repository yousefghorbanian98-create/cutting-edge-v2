// apps/desktop/src/components/patterns/StyleMatchWizard/StyleMatchWizard.tsx
// LOCK-01: STYLE MATCH = CORE
// LOCK-02: DEFAULT MODE = STYLE MATCH FLOW
// LOCK-03: 3-CLICK PROMISE (Step 1, 2, 3)
// LOCK-00: OSS-FIRST - ONLY IMPORT LIBRARIES
// LOCK-08: CLEAN SLATE
// LOCK-17: 13 GREEN CRITERIA
// LOCK-18: 11 AUTO-FAILURE CONDITIONS

import { Stepper, Step, StepLabel } from "@/components/ui/stepper"
import { TimelineEditor } from "react-timeline-editor"
import { Card } from "@/components/ui/card"

export function StyleMatchWizard() {
  return (
    <Card className="w-full max-w-4xl mx-auto">
      <Stepper activeStep={0}>
        <Step>
          <StepLabel>Reference Selection</StepLabel>
        </Step>
        <Step>
          <StepLabel>Source Clips</StepLabel>
        </Step>
        <Step>
          <StepLabel>Preferences & Generate</StepLabel>
        </Step>
      </Stepper>
      <TimelineEditor />
    </Card>
  )
}
