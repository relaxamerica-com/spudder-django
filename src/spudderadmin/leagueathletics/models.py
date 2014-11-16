from collections import OrderedDict
from decimal import Decimal
import json
from django.db import models
from spudderdomain.models import SingletonModel
from spudmart.upload.models import UploadedFile


class LeagueAthleticsImport(SingletonModel):
    zip_codes_file = models.ForeignKey(UploadedFile, null=True)
    in_progress = models.BooleanField(default=False)
    progress = models.FloatField(default=0.00)
    statistics = models.TextField(blank=True, default='')
    current_line = models.IntegerField(default=0)

    def __init__(self, *args, **kw):
        super(LeagueAthleticsImport, self).__init__(*args, **kw)

    def save(self, *args, **kw):
        super(LeagueAthleticsImport, self).save(*args, **kw)

    def clear(self):
        self.zip_codes_file = None
        self.in_progress = False
        self.progress = 0.00
        self.statistics = ''
        self.current_line = 0

    def update_progress(self, row):
        processed_piece = (len(row) * 1.0) / self.zip_codes_file.file.file.blobstore_info.size
        self.progress += processed_piece

    def get_statistics(self):
        if not self.statistics:
            return {}

        statistics_json = json.loads(self.statistics)
        statistics = OrderedDict(sorted(statistics_json.items()))

        return statistics

    def update_statistics(self, zip_code, total, imported):
        statistics = self.get_statistics()
        statistics[zip_code] = {
            'total': total,
            'imported': imported,
            'omitted': total - imported
        }

        self.statistics = json.dumps(statistics)