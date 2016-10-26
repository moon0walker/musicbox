"""
    Central storage of application and user settings
"""

from __future__ import with_statement
from configparser import (
    RawConfigParser,
    NoSectionError,
    NoOptionError
)
import logging
import os
import sys

from gi.repository import GLib

logger = logging.getLogger(__name__)

def _glib_wait_inner(timeout, glib_timeout_func):
    id = [None] # Have to hold the value in a mutable structure because
                # python's scoping rules prevent us assigning to an
                # outer scope directly.
    def waiter(function):
        def thunk(*args, **kwargs):
            id[0] = None
            return function(*args, **kwargs)
        def delayer(*args, **kwargs):
            if id[0]: GLib.source_remove(id[0])
            id[0] = glib_timeout_func(timeout, thunk, *args, **kwargs)
        return delayer
    return waiter

def glib_wait(timeout):
    """
        Decorator to make a function run only after 'timeout'
        milliseconds have elapsed since the most recent call to the
        function.

        For example, if a function was given a timeout of 1000 and
        called once, then again half a second later, it would run
        only once, 1.5 seconds after the first call to it.

        Arguments are supported, but which call's set of arguments
        is used is undefined, so this is not useful for much beyond
        passing in unchanging arguments like 'self' or 'cls'.

        If the function returns a value that evaluates to True, it
        will be called again under the same timeout rules.
    """
    # 'undefined' is a bit of a white lie - it's always the most
    # recent call's args. However, I'm reserving the right to change
    # the implementation later for the moment, and really I don't
    # think it makes sense to use functions that have changing args
    # with this decorator.
    return _glib_wait_inner(timeout, GLib.timeout_add)

def glib_wait_seconds(timeout):
    """
        Same as glib_wait, but uses GLib.timeout_add_seconds instead
        of GLib.timeout_add and takes its timeout in seconds. See the
        glib documention for why you might want to use one over the
        other.
    """
    return _glib_wait_inner(timeout, GLib.timeout_add_seconds)

TYPE_MAPPING = {
    'I': int,
    'S': str,
    'F': float,
    'B': bool,
    'L': list,
    'D': dict,
    'U': str
}

class SettingsManager(RawConfigParser):
    settings = None
    __version__ = 1

    def __init__(self, location=None, default_location=None):
        """
            Sets up the settings manager. Expects a location
            to a file where settings will be stored. Also sets up
            periodic saves to disk.

            :param location: the location to save the settings to,
                settings will never be stored if this is None
            :type location: str or None
            :param default_location: the default location to
                initialize settings from
        """
        RawConfigParser.__init__(self)

        self.location = location
        self._saving = False
        self._dirty = False

        if default_location is not None:
            try:
                self.read(default_location)
            except:
                pass

        if location is not None:
            try:
                self.read(self.location) or \
                    self.read(self.location + ".new") or \
                    self.read(self.location + ".old")
            except:
                pass

        if self.get_option('settings/version', 0) is None:
            self.set_option('settings/version', self.__version__)

        # save settings every 30 seconds
        if location is not None:
            self._timeout_save()

    @glib_wait_seconds(30)
    def _timeout_save(self):
        """Save every 30 seconds"""
        self.save()
        return True

    def copy_settings(self, settings):
        """
            Copies one all of the settings contained
            in this instance to another

            :param settings: the settings object to copy to
            :type settings: :class:`xl.settings.SettingsManager`
        """
        for section in self.sections():
            for (key, value) in self.items(section):
                settings._set_direct('%s/%s' % (section, key), value)

    def clone(self):
        """
            Creates a copy of this settings object
        """
        settings = SettingsManager(None)
        self.copy_settings(settings)
        return settings

    def set_option(self, option, value, save=False):
        """
            Set an option (in ``section/key`` syntax) to the specified value

            :param option: the full path to an option
            :type option: string
            :param value: the value the option should be assigned
            :type value: any
            :param save: If True, cause the settings to be written to file
        """
        value = self._val_to_str(value)
        splitvals = option.split('/')
        section, key = "/".join(splitvals[:-1]), splitvals[-1]

        try:
            self.set(section, key, value)
        except NoSectionError:
            self.add_section(section)
            self.set(section, key, value)

        self._dirty = True
        
        if save:
            self.delayed_save()

        section = section.replace('/', '_')

        # event.log_event('option_set', self, option)
        # event.log_event('%s_option_set' % section, self, option)

    def get_option(self, option, default=None):
        """
            Get the value of an option (in ``section/key`` syntax),
            returning *default* if the key does not exist yet

            :param option: the full path to an option
            :type option: string
            :param default: a default value to use as fallback
            :type default: any
            :returns: the option value or *default*
            :rtype: any
        """
        splitvals = option.split('/')
        section, key = "/".join(splitvals[:-1]), splitvals[-1]

        try:
            value = self.get(section, key)
            value = self._str_to_val(value)
        except NoSectionError:
            value = default
        except NoOptionError:
            value = default

        return value

    def has_option(self, option):
        """
            Returns information about the existence
            of a particular option

            :param option: the option path
            :type option: string
            :returns: whether the option exists or not
            :rtype: bool
        """
        splitvals = option.split('/')
        section, key = "/".join(splitvals[:-1]), splitvals[-1]

        return RawConfigParser.has_option(self, section, key)

    def remove_option(self, option):
        """
            Removes an option (in ``section/key`` syntax),
            thus will not be saved anymore

            :param option: the option path
            :type option: string
        """
        splitvals = option.split('/')
        section, key = "/".join(splitvals[:-1]), splitvals[-1]

        RawConfigParser.remove_option(self, section, key)

    def _set_direct(self, option, value):
        """
            Sets the option directly to the value,
            only for use in copying settings.

            :param option: the option path
            :type option: string
            :param value: the value to set
            :type value: any
        """
        splitvals = option.split('/')
        section, key = "/".join(splitvals[:-1]), splitvals[-1]

        try:
            self.set(section, key, value)
        except NoSectionError:
            self.add_section(section)
            self.set(section, key, value)

        # event.log_event('option_set', self, option)

    def _val_to_str(self, value):
        """
            Turns a value of some type into a string so it
            can be a configuration value.
        """
        for k, v in TYPE_MAPPING.items():
            if v == type(value):
                if v == list:
                    return k + ": " + repr(value)
                else:
                    return k + ": " + str(value)

        # raise ValueError(_("We don't know how to store that "
        #     "kind of setting: "), type(value))

    def _str_to_val(self, value):
        """
            Convert setting strings back to normal values.
        """
        try:
            kind, value = value.split(': ', 1)
        except ValueError:
            return ''

        # Lists and dictionaries are special case
        if kind in ('L', 'D'):
            return eval(value)

        if kind in TYPE_MAPPING.keys():
            if kind == 'B':
                if value != 'True':
                    return False

            try:
                value = TYPE_MAPPING[kind](value)
            except:
                pass

            return value
        else:
            raise ValueError(_("An Unknown type of setting was found!"))

    # @glib_wait(200)
    def delayed_save(self):
        '''Save options after a delay, waiting for multiple saves to accumulate'''
        self.save()

    def save(self):
        """
            Save the settings to disk
        """
        if self.location is None:
            logger.debug("Save requested but not saving settings, "
                "location is None")
            return

        if self._saving or not self._dirty:
            return

        self._saving = True

        logger.debug("Saving settings...")

        with open(self.location + ".new", 'w') as f:
            self.write(f)

            try:
                # make it readable by current user only, to protect private data
                os.fchmod(f.fileno(), 384)
            except:
                pass # fail gracefully, eg if on windows

            f.flush()

        try:
            os.rename(self.location, self.location + ".old")
        except:
            pass # if it doesn'texist we don't care

        os.rename(self.location + ".new", self.location)

        try:
            os.remove(self.location + ".old")
        except:
            pass

        self._saving = False
        self._dirty = False

        os.system( "cp /home/user/musicbox/settings.ini /home/user/musicbox/data/settings.ini.bak" )
        os.system( "cp -r /home/user/musicbox/data/banner/* /home/user/musicbox/data/banner_bak/*" )


# MANAGER = SettingsManager("settings.ini")

# get_option = MANAGER.get_option
# set_option = MANAGER.set_option
 