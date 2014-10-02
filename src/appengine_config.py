import logentries
from spudderadmin.templatetags.featuretags import feature_is_enabled

if feature_is_enabled('logentries_logging'):
    logentries.init('fe9682cd-b7db-4d3d-8c09-b435e3534aeb', 'SpudderLive/event.log')
