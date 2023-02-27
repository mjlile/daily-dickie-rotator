# daily-dickie-video-rotator Lambda

This Lambda code rotates videos in an s3 bucket. These videos are displayed on dailydickie.mjlile.com. It finds the next video to share, and (unless using preview mode) updates the target, plus the candidate shared-on metadata. Trigger this Lambda via EventBridge schedule to update the site's video. This Lambda just operates on the objects - the objects could be anything and used for whatever. It does assume the rotation period is 1 day or longer. To support shorter periods, set a finer grained `shared-on` timestamp.

## Input format

```json
{
  "srcPrefix": "dickie-videos",
  "targetKey": "today.webm",
  "preview": "true"
}
```

- `srcPrefix` - the prefix in the s3 bucket under which the candidate objects live.
- `targetKey` - the key that candidate will be copied to. Does not include `srcPrefix`.
- `preview` - if true, preview the operation but do not update anything in s3.