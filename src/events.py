
class TrackingPixelEvents(object):
    USER_REGISTERED = 'user_registered'
    CHALLENGER_USER_REGISTERER = 'challenger_user_registered'
    CHALLENGE_ACCEPTED = 'challenge_accepted'


TRACKING_PIXEL_CONF = {
    TrackingPixelEvents.USER_REGISTERED: [
        'components/tracking_pixels/brainwave_media_tracking_pixel.html'
    ],
    TrackingPixelEvents.CHALLENGER_USER_REGISTERER: [
        'components/tracking_pixels/challenger_user_registration.html'
    ],
    TrackingPixelEvents.CHALLENGE_ACCEPTED: [
        'components/tracking_pixels/successful_challenge_submission.html'
    ]
}
