from datetime import datetime

from pydantic import BaseModel


class Audio(BaseModel):
	id: str
	minio_key: str
	created: datetime
	modified: datetime
	status: str

	@staticmethod
	async def refresh() -> int:
		"""
		This method handles all the logic to update the Audiofiles from
		minio that are not already present in the mongodb

		@returns: int, the number of new files added to the mongodb
		"""
		pass
