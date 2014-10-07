FEATURES = {
    'dev': [
        'spud_tagging',
        'manage_team_admins',
        'clubs',
        'nays_survey',
        'affiliate_login',  # just login & dashboard page    
        'invite_clubs',
        'challenges_landing_page',
        'challenges_only_override'
        'challenge_challenge',
        'challenge_register_club'
        'challenge_tree',
        'email_error_logs',
    ],
    'stage': [
        'spud_tagging',
        'manage_team_admins',
        'clubs',
        'nays_survey',
        'affiliate_login',
        'invite_clubs',
        'challenges_landing_page',
        'challenges_only_override',
        'challenge_challenge',
        'challenge_register_club',
        'challenge_tree',
        'email_error_logs',
    ],
    'live': [
        'google_analytics',
        'alexa_analytics',
        'spud_tagging'
        'challenges_landing_page',
        'challenges_only_override',  # Prevent access to any other part of spudder
        'challenge_challenge',
    ]
}
