=========
Changelog
=========

.. versionadded:: 0.1.2
   Added the UploadURL table to the database
   

.. versionadded:: 0.1.1
   All database models now inherit from the :class:`models.meta.InnoDBMix` object
   This defines some global parameters such as creating all new tables using InnoDB
   Additionally global functions have been moved to the superclass

.. versionadded:: 0.1.0
   Several changes here.

   * Models merged with the basestation code
   * Backrefs moved to the parent classes
   * Unittesting added

.. versionchanged:: 0.1.0
   Backrefs in the House and Deployment to the relvant metadata tables
   were called metadata,  this was causing problems with SQLA

   These backrefs have now meen named <class>.meta
     
.. versionadded:: 0.0
   Initial Release


