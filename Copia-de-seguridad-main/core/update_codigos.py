from core.models import Arancel

for arancel in Arancel.objects.all():
    arancel.save()