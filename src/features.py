FEATURES = {
    'dev': [
        'spud_tagging',
        'manage_team_admins',
        'clubs',
        'nays_survey',
        'affiliate_login',  # just login & dashboard page    
        'invite_clubs',
        'challenges_landing_page',
        'challenges_only_override',
        # 'challenge_challenge',
        'challenge_register_club',
        'challenge_tree',
        'email_error_logs',
        'tracking_pixels',
        'challenge_management',
        'challenge_dreamsforkids_piechallenge',
        'challenge_livetest',  # this is only for testing stripe
    ],
    'stage': [
        # 'spud_tagging',
        # 'manage_team_admins',
        # 'clubs',
        # 'nays_survey',
        # 'affiliate_login',
        # 'invite_clubs',
        'challenges_landing_page',
        'challenges_only_override',
        # 'challenge_challenge',
        # 'challenge_register_club',
        'challenge_tree',
        'email_error_logs',
        'tracking_pixels',
        # 'stripe_ein_validation',
        'all_fans_auto_follow_main_spudder_fan',
        'challenge_dreamsforkids_piechallenge',
        'challenge_livetest',  # this is only for testing stripe
    ],
    'live': [
        'google_analytics',
        'alexa_analytics',
        # 'spud_tagging',
        'challenges_landing_page',
        'challenges_only_override',  # Prevent access to any other part of spudder
        'email_error_logs',
        'tracking_pixels',
        'all_fans_auto_follow_main_spudder_fan',
        # 'challenge_challenge',
        'challenge_dreamsforkids_piechallenge',
    ]
}


