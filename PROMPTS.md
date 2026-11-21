# Paste-ready prompts

Two steps for every shot:

1. **Still image**: model **Z-Image Turbo**, 1280x720, 8 steps, guidance 0.
2. **Animate it**: model **Wan2.2 TextImage2video FastWan 5B**. Choose *Start
   video with image*, drop in the still from step 1, set 832x480 for drafts
   (1280x704 for final), 97 frames (4s), 3 steps.

Use the same negative prompt everywhere:

```
humans, people, person, human hands, human face, text, watermark, logo, blurry, distorted anatomy, extra limbs, extra legs, deformed paws, flicker, low quality
```

---

## 0. Character sheet (do this first)
Generate 8–10 of these and keep the best one. Use it as the "this is Hammi"
reference: compare every later still against it, and feed it to Flux Klein /
Qwen Edit as a reference image if your stills start drifting off-model.

```
Character turnaround sheet of Hammi, an anthropomorphic Pembroke Welsh corgi with a red-headed tri-color coat (deep mahogany copper-red head and ears with pale cream insides, a white blaze up the middle of the face widening into a white muzzle and white lower cheeks, white chest, black fur visible at the back of the neck and on the hips below the sweater, copper-red legs, white paws), a sturdy chunky corgi build, soulful dark eyes and big upright ears, wearing a mustard-yellow knit sweater and a small forest-green scarf, standing upright on hind legs, front view, side view and back view, neutral pose, plain warm cream background. stylized 3D animated film, soft warm lighting, rounded shapes, rich textures, pastel and warm autumn color palette
```

## 1. Washing dishes
**Still**
```
Hammi, an anthropomorphic Pembroke Welsh corgi with a red-headed tri-color coat (deep mahogany copper-red head and ears with pale cream insides, a white blaze up the middle of the face widening into a white muzzle and white lower cheeks, white chest, black fur visible at the back of the neck and on the hips below the sweater, copper-red legs, white paws), a sturdy chunky corgi build, soulful dark eyes and big upright ears, wearing a mustard-yellow knit sweater and a small forest-green scarf. Hammi standing on a small wooden step stool at the kitchen sink washing a plate with a yellow sponge, soap bubbles, window above the sink with morning light and autumn trees. stylized 3D animated film, cozy storybook town, soft warm lighting, gentle depth of field, rounded shapes, rich textures, pastel and warm autumn color palette, cinematic composition
```
**Motion**
```
Hammi, an anthropomorphic Pembroke Welsh corgi with a red-headed tri-color coat (deep mahogany copper-red head and ears with pale cream insides, a white blaze up the middle of the face widening into a white muzzle and white lower cheeks, white chest, black fur visible at the back of the neck and on the hips below the sweater, copper-red legs, white paws), a sturdy chunky corgi build, soulful dark eyes and big upright ears, wearing a mustard-yellow knit sweater and a small forest-green scarf. Hammi scrubs the plate in slow circles with the sponge, soap bubbles float up and pop, water runs from the faucet. Static camera from behind the window. stylized 3D animated film, cozy storybook town, soft warm lighting, gentle depth of field, rounded shapes, rich textures, pastel and warm autumn color palette, cinematic composition
```

## 2. Morning coffee
**Still**
```
Hammi, an anthropomorphic Pembroke Welsh corgi with a red-headed tri-color coat (deep mahogany copper-red head and ears with pale cream insides, a white blaze up the middle of the face widening into a white muzzle and white lower cheeks, white chest, black fur visible at the back of the neck and on the hips below the sweater, copper-red legs, white paws), a sturdy chunky corgi build, soulful dark eyes and big upright ears, wearing a mustard-yellow knit sweater and a small forest-green scarf. Warm cluttered cottage kitchen, Hammi standing upright at the counter pouring coffee from a small kettle into a big blue mug, hanging plants, steam rising, window over the sink showing autumn trees. stylized 3D animated film, cozy storybook town, soft warm lighting, gentle depth of field, rounded shapes, rich textures, pastel and warm autumn color palette, cinematic composition
```
**Motion**
```
Hammi, an anthropomorphic Pembroke Welsh corgi with a red-headed tri-color coat (deep mahogany copper-red head and ears with pale cream insides, a white blaze up the middle of the face widening into a white muzzle and white lower cheeks, white chest, black fur visible at the back of the neck and on the hips below the sweater, copper-red legs, white paws), a sturdy chunky corgi build, soulful dark eyes and big upright ears, wearing a mustard-yellow knit sweater and a small forest-green scarf. Hammi carefully pours steaming coffee into the blue mug, steam curls upward, leaves sway outside the window. Slow side dolly. stylized 3D animated film, cozy storybook town, soft warm lighting, gentle depth of field, rounded shapes, rich textures, pastel and warm autumn color palette, cinematic composition
```

## 3. Going to work (walking through town)
**Still**
```
Hammi, an anthropomorphic Pembroke Welsh corgi with a red-headed tri-color coat (deep mahogany copper-red head and ears with pale cream insides, a white blaze up the middle of the face widening into a white muzzle and white lower cheeks, white chest, black fur visible at the back of the neck and on the hips below the sweater, copper-red legs, white paws), a sturdy chunky corgi build, soulful dark eyes and big upright ears, wearing a mustard-yellow knit sweater and a small forest-green scarf. Wide shot of a cobblestone street in Pawsley Hollow, autumn trees, small animal-sized shopfronts, hanging lanterns, a clock tower in the distance, Hammi walking upright along the sidewalk with a leather satchel. stylized 3D animated film, cozy storybook town, soft warm lighting, gentle depth of field, rounded shapes, rich textures, pastel and warm autumn color palette, cinematic composition
```
**Motion**
```
Hammi, an anthropomorphic Pembroke Welsh corgi with a red-headed tri-color coat (deep mahogany copper-red head and ears with pale cream insides, a white blaze up the middle of the face widening into a white muzzle and white lower cheeks, white chest, black fur visible at the back of the neck and on the hips below the sweater, copper-red legs, white paws), a sturdy chunky corgi build, soulful dark eyes and big upright ears, wearing a mustard-yellow knit sweater and a small forest-green scarf. Hammi walks along the sidewalk toward the camera, leaves swirl in a gentle breeze, a shop sign swings. Slow tracking shot. stylized 3D animated film, cozy storybook town, soft warm lighting, gentle depth of field, rounded shapes, rich textures, pastel and warm autumn color palette, cinematic composition
```

## 4. Catching the bus (with Dwight the otter)
**Still**
```
Hammi, an anthropomorphic Pembroke Welsh corgi with a red-headed tri-color coat (deep mahogany copper-red head and ears with pale cream insides, a white blaze up the middle of the face widening into a white muzzle and white lower cheeks, white chest, black fur visible at the back of the neck and on the hips below the sweater, copper-red legs, white paws), a sturdy chunky corgi build, soulful dark eyes and big upright ears, wearing a mustard-yellow knit sweater and a small forest-green scarf; Dwight, a sleek brown river otter in a navy bus-driver cap and vest. A small round vintage green bus pulling up to a wooden bus stop on a cobblestone street, the otter visible at the wheel, Hammi waiting on the bench, autumn morning. stylized 3D animated film, cozy storybook town, soft warm lighting, gentle depth of field, rounded shapes, rich textures, pastel and warm autumn color palette, cinematic composition
```
**Motion**
```
The bus rolls to a gentle stop, the doors fold open, the otter driver tips his cap, Hammi hops up from the bench. Static wide shot. stylized 3D animated film, cozy storybook town, soft warm lighting, gentle depth of field, rounded shapes, rich textures, pastel and warm autumn color palette, cinematic composition
```

---

## Writing your own
Template: `[character token]. [one setting + one action, concrete nouns]. [style lock]`

- **Still prompts** describe a *frozen moment*: pose, place, light.
- **Motion prompts** describe *one* slow action plus a camera move ("static",
  "slow push-in", "slow side dolly"). Two actions max. Ambient motion (steam,
  leaves, bubbles, dust motes) makes a shot feel alive for free.
- Avoid: fast action, hands holding small objects very close up, text/signs,
  more than 3 characters in frame.

All 16 shots of Episode 1 are in `episodes/ep01_morning_routine.json`.
`build.py` expands them into full prompts like the ones above.
