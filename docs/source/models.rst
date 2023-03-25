Working with models (schemas)
============================

A schema is like a frame where you define your data and how you want it to be.

.. code-block :: python

	from willpyre.schema import (
		schema, 
		Conint, 
		Constr,
		populate_schema,
		schema_to_json,
		validate_json,
		ValidationError,
	)


	@schema
	class Ok:
	    var: Conint(1, 2) = 21
	    random: int = 1


	@schema
	class User:
	    name: Constr(4, 250)
	    usertag: Constr(4, 100)


	@schema
	class Event:
	    title: str
	    description: str

The first line here imports the `schema` function and the types Conint and Constr.

The schema function is used as a `decorator <https://www.programiz.com/python-programming/decorator>`_. If you want to define any class as a schema, you **need to** use the schema decorator.

For the fields, there has to be a type annotation. You can add a default through ``=`` if you want.


Loading JSON from Schema
-------------------------

You can set values for fields in a schema from the data you want.

.. code-block :: python

	# print(
		# schema_to_json(
		# 	populate_schema(User, name="User1", 
		# 	usertag='user1',
		# 	),
		# )

If you uncomment this code and run it, you will get:

.. code-block :: python

	{ "name":"User1", "usertag": "user1"}

Explanation:
``populate_schema`` takes the first argument as schema class and the rest of the arguments are the fields and their respective values. It will return a schema object with the given values of fields. If you specify some fields that are not there in the schema, those fields will be ignored.
Then, you convert that schema to a dictionary object through the ``schema_to_json`` function.

Validating JSON Against a Schema
--------------------------------

When you accept arbitrary input from users, you may need to check if they are valid. Willpyre has a utility for this. After importing the ``validate_json`` function from ``willpyre.schema`` you can use that function to validate some data against a given schema.

.. code-block :: python

	validate_json(User, { "name":"User1", "usertag": "user1"})
	# validate_json(schema, data)

We are validating ``{ "name":"User1", "usertag": "user1"}`` with respect to User and it will return:

.. code-block :: python

	{ "name":"User1", "usertag": "user1"}

This function checks if the data is valid with respect to the given schema. If not, it throws a ``ValidationError`` which can be imported from ``willpyre.schema``.