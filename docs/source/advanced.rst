Advanced
========

This sheet contains **slightly** concepts, (comparative to the others given in the tutoial).

Extending the Router
--------------------

The classes on which the framework is based are highly customisable.
You can customise them to meet your specific needs.

Router
------
The Router class actually has a lot.
To extend it, you can customise as per your need. For instance, consider that you need a vary fast url-router(C-implementation or Cythonised one) due to some reason.

Then, remember that it must your Router must have a  ``handle`` method, that accepts a ``request`` parameter and ``response`` parameter, and must return an instance of ``structure.Response``. 
