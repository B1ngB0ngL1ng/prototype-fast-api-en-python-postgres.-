from app.repositories.resource_repository import ResourceRepository

class ResourceService:
    def __init__(self, db, resource):
        self.repo = ResourceRepository(db, resource)
    def list(self, limit, offset):
        return self.repo.list(limit, offset)
    def get(self, identifier):
        return self.repo.get(identifier)
    def create(self, body):
        return self.repo.create(body)
    def update(self, identifier, body):
        return self.repo.update(identifier, body)
    def delete(self, identifier):
        return self.repo.delete(identifier)
    def children(self, field, identifier, limit, offset):
        return self.repo.list(limit, offset, field, identifier)
