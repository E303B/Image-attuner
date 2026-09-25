# Image-attuner
Attunes images to another, making quite mesmerizing art

Uses config for following:
[EN]
- "attunementFile" - path to the image file which will be used for mapping colors (autoscales)
- "input" - path to the image which will be processed
- "output" - path to the output
- "seekRange" - area of 2n+1 square where n equals value of this key will be checked around each pixel
- "round" - boolean for whether to look only for colors in a circle, not a rectangle
- "precision" - lower the amount of different colors in the input file proportionally to precision. E.g, precision equal to 5.0 will lower the amount of colors 5 times. This WILL ONLY work if you have a lot of different colors. Used for optimization
- "method" - "full" - attune whole image/"box" - attune rectangle starting at ("startX";"startY") and ending at ("endX";"endY")
