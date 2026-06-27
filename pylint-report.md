# Pylint report

Pylint gives the following report:

```
************* Module app
app.py:27:0: C0116: Missing function or method docstring (missing-function-docstring)
app.py:36:0: C0116: Missing function or method docstring (missing-function-docstring)
app.py:52:0: C0116: Missing function or method docstring (missing-function-docstring)
app.py:57:0: C0116: Missing function or method docstring (missing-function-docstring)
app.py:66:0: C0116: Missing function or method docstring (missing-function-docstring)
app.py:80:0: C0116: Missing function or method docstring (missing-function-docstring)
app.py:105:0: C0116: Missing function or method docstring (missing-function-docstring)
app.py:113:0: C0116: Missing function or method docstring (missing-function-docstring)
app.py:113:0: R0911: Too many return statements (7/6) (too-many-return-statements)
app.py:154:0: C0116: Missing function or method docstring (missing-function-docstring)
app.py:180:0: C0116: Missing function or method docstring (missing-function-docstring)
app.py:192:0: C0116: Missing function or method docstring (missing-function-docstring)
app.py:218:0: C0116: Missing function or method docstring (missing-function-docstring)
app.py:227:0: C0116: Missing function or method docstring (missing-function-docstring)
app.py:263:0: C0116: Missing function or method docstring (missing-function-docstring)
app.py:290:0: C0116: Missing function or method docstring (missing-function-docstring)
app.py:319:0: C0116: Missing function or method docstring (missing-function-docstring)
app.py:381:0: C0116: Missing function or method docstring (missing-function-docstring)
app.py:407:0: C0116: Missing function or method docstring (missing-function-docstring)
app.py:447:0: C0116: Missing function or method docstring (missing-function-docstring)
************* Module authentication
authentication.py:8:0: C0116: Missing function or method docstring (missing-function-docstring)
authentication.py:15:0: C0116: Missing function or method docstring (missing-function-docstring)
authentication.py:23:0: C0116: Missing function or method docstring (missing-function-docstring)
authentication.py:30:0: C0116: Missing function or method docstring (missing-function-docstring)
authentication.py:35:0: C0116: Missing function or method docstring (missing-function-docstring)
authentication.py:41:0: C0116: Missing function or method docstring (missing-function-docstring)
authentication.py:45:0: C0116: Missing function or method docstring (missing-function-docstring)
authentication.py:49:0: C0116: Missing function or method docstring (missing-function-docstring)
************* Module categories
categories.py:6:0: C0116: Missing function or method docstring (missing-function-docstring)
categories.py:11:0: C0116: Missing function or method docstring (missing-function-docstring)
************* Module comments
comments.py:6:0: C0116: Missing function or method docstring (missing-function-docstring)
comments.py:11:0: C0116: Missing function or method docstring (missing-function-docstring)
comments.py:26:0: C0116: Missing function or method docstring (missing-function-docstring)
comments.py:34:0: C0116: Missing function or method docstring (missing-function-docstring)
comments.py:39:0: C0116: Missing function or method docstring (missing-function-docstring)
************* Module db
db.py:6:0: C0116: Missing function or method docstring (missing-function-docstring)
db.py:12:0: C0116: Missing function or method docstring (missing-function-docstring)
db.py:19:0: C0116: Missing function or method docstring (missing-function-docstring)
db.py:22:0: C0116: Missing function or method docstring (missing-function-docstring)
************* Module links
links.py:6:0: C0116: Missing function or method docstring (missing-function-docstring)
links.py:11:0: C0116: Missing function or method docstring (missing-function-docstring)
links.py:27:0: C0116: Missing function or method docstring (missing-function-docstring)
links.py:39:0: C0116: Missing function or method docstring (missing-function-docstring)
links.py:53:0: C0116: Missing function or method docstring (missing-function-docstring)
links.py:60:0: C0116: Missing function or method docstring (missing-function-docstring)
links.py:68:0: C0116: Missing function or method docstring (missing-function-docstring)
links.py:73:0: C0116: Missing function or method docstring (missing-function-docstring)
links.py:93:0: C0116: Missing function or method docstring (missing-function-docstring)
links.py:121:0: C0116: Missing function or method docstring (missing-function-docstring)
links.py:137:0: C0116: Missing function or method docstring (missing-function-docstring)
************* Module pagination
pagination.py:6:0: C0116: Missing function or method docstring (missing-function-docstring)
************* Module seed
seed.py:29:0: C0116: Missing function or method docstring (missing-function-docstring)
seed.py:35:0: C0116: Missing function or method docstring (missing-function-docstring)
seed.py:41:0: C0116: Missing function or method docstring (missing-function-docstring)
seed.py:63:0: C0116: Missing function or method docstring (missing-function-docstring)
seed.py:70:0: C0116: Missing function or method docstring (missing-function-docstring)
seed.py:97:0: C0116: Missing function or method docstring (missing-function-docstring)
seed.py:104:0: C0116: Missing function or method docstring (missing-function-docstring)
seed.py:127:0: C0116: Missing function or method docstring (missing-function-docstring)
************* Module users
users.py:7:0: C0116: Missing function or method docstring (missing-function-docstring)
users.py:13:0: C0116: Missing function or method docstring (missing-function-docstring)
users.py:23:0: C0116: Missing function or method docstring (missing-function-docstring)
users.py:29:0: C0116: Missing function or method docstring (missing-function-docstring)
************* Module validators
validators.py:18:0: C0116: Missing function or method docstring (missing-function-docstring)
validators.py:22:0: C0116: Missing function or method docstring (missing-function-docstring)
validators.py:38:0: C0116: Missing function or method docstring (missing-function-docstring)
validators.py:48:0: C0116: Missing function or method docstring (missing-function-docstring)
validators.py:61:0: C0116: Missing function or method docstring (missing-function-docstring)
validators.py:74:0: C0116: Missing function or method docstring (missing-function-docstring)
validators.py:81:0: C0116: Missing function or method docstring (missing-function-docstring)
validators.py:94:0: C0116: Missing function or method docstring (missing-function-docstring)

------------------------------------------------------------------
Your code has been rated at 8.72/10 (previous run: 8.72/10, +0.00)
```

The following sections describe the remaining warnings and explain why they were not changed in the application.

## Function docstring warnings

Most of the remaining Pylint warnings are of the following type:

```
C0116: Missing function or method docstring (missing-function-docstring)
```

These warnings concern individual functions that do not have separate docstring comments.

The application now uses module-level docstrings at the beginning of Python files, but function-level docstrings were not added to every function. This was a conscious decision, as the project is a small course application, and many functions are route handlers or short database helper functions. In these cases, the function name, route decorator and surrounding module usually describe the purpose of the function clearly enough. Adding a separate docstring to every function would therefore have added a large amount of repetitive text without necessarily improving readability.

For this reason, the remaining `missing-function-docstring` warnings were left in the final Pylint report.

## Too many return statements

Pylint also reports the following warning for the registration route:

```
R0911: Too many return statements (7/6) (too-many-return-statements)
```

This warning is related to the `register` function, which validates several possible error cases, such as an invalid username, an invalid password, non-matching passwords and an already existing username.

The function returns the registration form immediately when a validation error is found. This makes the validation straightforward and easy to test, because each error case is handled close to the related validation check.

The route could alternatively be refactored to reduce the number of return statements, but this would not necessarily make the code easier to read. For this reason, the structure was kept as it is.

