import psycopg2
import psycopg2.sql as sql

class Storage:
	def __init__(self, url):
		self.connection = None
		self.database_url = url
		self.connect()

	def connect(self):
		self.connection = psycopg2.connect(self.database_url)
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

	def fetch_all_aliases(self):
		return self.execute("SELECT * FROM aliases")

	def fetch_guild_aliases(self, snowflake: int):
		return self.execute("SELECT alias, clan FROM aliases WHERE snowflake = %s ORDER BY alias ASC", [snowflake])

	def link_guild(self, snowflake: int, alias: str, clan: str):
		self.execute("INSERT INTO aliases (snowflake, alias, clan, last_used) VALUES (%s, %s, %s, current_date)", [snowflake, alias, clan])

	def unlink_guild(self, snowflake: int, alias: str):
		self.execute("DELETE FROM aliases WHERE snowflake = %s AND alias = %s", [snowflake, alias])

	def update_last_used(self, snowflake: int, alias: str):
		self.execute("UPDATE aliases SET last_used = current_date WHERE snowflake = %s AND alias = %s", [snowflake, alias])