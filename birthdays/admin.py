from django.contrib import admin

from birthdays.models import (Person, NBASource, BIGSource, PhoneBookSource, WieOWieSource, WikiSource, SoccerSource,
                              SchoolBankSource, ActeursSpotSource, BenfCastingSource, BilliardSource, HockeySource,
                              KNACSource, TriathlonSource, MusicSocietySource, FiftyPlusSource, HobbyJournalSource)


class PersonAdmin(admin.ModelAdmin):
    list_display = ["full_name", "birth_date", "props"]


class PersonSourceAdmin(PersonAdmin):
    raw_id_fields = ["master"]


admin.site.register(Person, PersonAdmin)
admin.site.register(NBASource, PersonSourceAdmin)
admin.site.register(BIGSource, PersonSourceAdmin)
admin.site.register(PhoneBookSource, PersonSourceAdmin)
admin.site.register(WieOWieSource, PersonSourceAdmin)
admin.site.register(WikiSource, PersonSourceAdmin)
admin.site.register(SchoolBankSource, PersonSourceAdmin)
admin.site.register(SoccerSource, PersonSourceAdmin)
admin.site.register(ActeursSpotSource, PersonSourceAdmin)
admin.site.register(BenfCastingSource, PersonSourceAdmin)
admin.site.register(BilliardSource, PersonSourceAdmin)
admin.site.register(HockeySource, PersonSourceAdmin)
admin.site.register(KNACSource, PersonSourceAdmin)
admin.site.register(TriathlonSource, PersonSourceAdmin)
admin.site.register(MusicSocietySource, PersonSourceAdmin)
admin.site.register(FiftyPlusSource, PersonSourceAdmin)
admin.site.register(HobbyJournalSource, PersonSourceAdmin)
