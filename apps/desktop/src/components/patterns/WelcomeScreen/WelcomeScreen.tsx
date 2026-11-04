// apps/desktop/src/components/patterns/WelcomeScreen/WelcomeScreen.tsx
// LOCK-01: STYLE MATCH = CORE
// LOCK-02: DEFAULT MODE = STYLE MATCH FLOW
// LOCK-03: 3-CLICK PROMISE (Step 1: Match a Style)
// LOCK-00: OSS-FIRST - ONLY IMPORT LIBRARIES
// LOCK-08: CLEAN SLATE (No pre-v2.4 code)
// LOCK-17: 13 GREEN CRITERIA
// LOCK-18: 11 AUTO-FAILURE CONDITIONS

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group"
import { Sparkles } from "lucide-react"

export function WelcomeScreen() {
  return (
    <Card className="w-full max-w-2xl mx-auto">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Sparkles className="h-6 w-6 text-primary" />
          Match a Style (Step 1 of 3)
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <Button className="w-full">GET STARTED →</Button>
        <RadioGroup defaultValue="library">
          <div className="flex items-center space-x-2">
            <RadioGroupItem value="library" id="library" />
            <label htmlFor="library">From Library (20 bundled references)</label>
          </div>
          <div className="flex items-center space-x-2">
            <RadioGroupItem value="upload" id="upload" />
            <label htmlFor="upload">Upload Your Own</label>
          </div>
        </RadioGroup>
      </CardContent>
    </Card>
  )
}
