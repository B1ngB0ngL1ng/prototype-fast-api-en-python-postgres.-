from app.services.resource_service import ResourceService

class ResourceController:
    def __init__(self, db, resource):
        self.service = ResourceService(db, resource)
    def list(self, limit, offset):
        return self.service.list(limit, offset)
    def get(self, identifier):
        return self.service.get(identifier)
    def create(self, body):
        return self.service.create(body)
    def update(self, identifier, body):
        return self.service.update(identifier, body)
    def delete(self, identifier):
        return self.service.delete(identifier)
