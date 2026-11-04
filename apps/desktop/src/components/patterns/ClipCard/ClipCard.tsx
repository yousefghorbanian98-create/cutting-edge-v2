// apps/desktop/src/components/patterns/ClipCard/ClipCard.tsx
// LOCK-03: HOTCLIP -> MEDIAPIPE + FFMPEG + CLIP + LIBROSA (IMPORT ONLY)
// LOCK-00: OSS-FIRST - ONLY IMPORT LIBRARIES
// LOCK-08: CLEAN SLATE
// LOCK-17: 13 GREEN CRITERIA
// LOCK-18: 11 AUTO-FAILURE CONDITIONS

import { Card, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"

export function ClipCard({ filename, duration, type }) {
  return (
    <Card className="w-48 h-32 relative">
      <CardContent className="p-2">
        <Badge variant="secondary">{type}</Badge>
        <p className="text-xs truncate mt-1">{filename}</p>
        <p className="text-xs text-muted-foreground">{duration}</p>
      </CardContent>
    </Card>
  )
}
