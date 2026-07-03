from codealmanac.local.delivery.ledger.models import DeliveryRecord
from codealmanac.local.delivery.ledger.requests import (
    CreateDeliveryRequest,
    ReadDeliveryRequest,
    UpdateDeliveryRequest,
)
from codealmanac.local.delivery.ledger.store import DeliveriesStore


class DeliveriesService:
    def __init__(self, store: DeliveriesStore):
        self.store = store

    def create(self, request: CreateDeliveryRequest) -> DeliveryRecord:
        return self.store.create(request)

    def read(self, request: ReadDeliveryRequest) -> DeliveryRecord:
        return self.store.read(request)

    def update(self, request: UpdateDeliveryRequest) -> DeliveryRecord:
        return self.store.update(request)
