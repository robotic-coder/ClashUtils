import os
import psycopg2
import psycopg2.sql as sql

class Storage:
	def __init__(self):
		self.connection = None
		self.connect()

	def connect(self):
		self.connection = psycopg2.connect(os.environ["DATABASE_URL"])
		self.connection.autocommit = True

	def get_cursor(self):
		try:
			return self.connection.cursor()
		except psycopg2.InterfaceError:
			self.connect()
			return self.connection.cursor()

	def execute(self, query: str, values = []):
		cursor = self.get_cursor()
		cursor.execute(query, values)

		if cursor.description is None:
			return None

		results = cursor.fetchall()
		output = []
		for row in results:
			new_row = {}
			for i in range(0, len(row)):
				new_row[cursor.description[i].name] = row[i]
			output.append(new_row)
		return output

	def fetch_all_channels(self):
		return self.execute("SELECT * FROM channels")

	def link_channel(self, snowflake: int, prefix: str, clan: str):
		self.execute("INSERT INTO channels (snowflake, prefix, clan, last_used) VALUES (%s, %s, %s, current_date)", [snowflake, prefix, clan])

	def unlink_channel(self, snowflake: int, prefix: str):
		self.execute("DELETE FROM channels WHERE snowflake = %s AND prefix = %s", [snowflake, prefix])

	def update_last_used(self, snowflake: int, prefix: str):
		self.execute("UPDATE channels SET last_used = current_date WHERE snowflake = %s AND prefix = %s", [snowflake, prefix])