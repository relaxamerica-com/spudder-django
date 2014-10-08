from spudderdomain.controllers import EventController


TRACKING_PIXEL_CONF = {
    EventController.USER_REGISTERED: [
        'components/tracking_pixels/brainwave_media_tracking_pixel.html'
    ],
    EventController.CHALLENGER_USER_REGISTERER: [
        'components/tracking_pixels/challenger_user_registration.html'
    ],
    EventController.CHALLENGE_ACCEPTED: [
        'components/tracking_pixels/successful_challenge_submission.html'
    ]
}
