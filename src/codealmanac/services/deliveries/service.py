from codealmanac.services.deliveries.models import DeliveryRecord
from codealmanac.services.deliveries.requests import (
    CreateDeliveryRequest,
    ReadDeliveryRequest,
    UpdateDeliveryRequest,
)
from codealmanac.services.deliveries.store import DeliveriesStore


class DeliveriesService:
    def __init__(self, store: DeliveriesStore):
        self.store = store

    def create(self, request: CreateDeliveryRequest) -> DeliveryRecord:
        return self.store.create(request)

    def read(self, request: ReadDeliveryRequest) -> DeliveryRecord:
        return self.store.read(request)

    def update(self, request: UpdateDeliveryRequest) -> DeliveryRecord:
        return self.store.update(request)
