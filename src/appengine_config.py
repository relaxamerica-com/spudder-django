import logging

from spudderadmin.templatetags.featuretags import feature_is_enabled

if feature_is_enabled('logentries_inprocess_logging'):
    from logentries import logentriesinprocess as logentries
    logentries.init('fe9682cd-b7db-4d3d-8c09-b435e3534aeb', 'SpudderLive/event.log')
    logging.info("logentries_inprocess_logging enabled")

