#python
'''
'''

# Standard
import exceptions
import os
import profile
import pstats
import shlex
import sys
# Related
import lx
# Local

def parse_arguments():
    '''This code was copied from moopy and then slightly modified.
    '''
    
    # First we parse the arguments with shlex.
    raw_arguments = shlex.split(lx.arg())
    
    # Now take the parsed args, and loop through each item and split them
    # into two lists. arguments and keyword_arguments.
    # We also convert every arg, key, and value into the basic proper python
    # objects.
    arguments = []
    keyword_arguments = {}
    def convert_string(string_to_convert):
        '''We use this function to quickly convert a string into an int,
        float, or bool. If it is found to not be a bool, int, or float,
        the string is returned unedited.
        '''
        try:
            if '.' in string_to_convert:
                return float(string_to_convert)
            else:
                return int(string_to_convert)
        except ValueError:
            if string_to_convert.lower() == 'true':
                return True
            if string_to_convert.lower() == 'false':
                return False
            else:
                return string_to_convert
            
    for raw_argument in raw_arguments:
        if '=' in raw_argument:
            # If there is a = character, its a kw_arg
            
            split_raw_argument = raw_argument.split('=', 1)
            
            # Both the key and the value, we use
            # convert_string() to make sure the objects are their intended
            # type.
            key = convert_string(split_raw_argument[0])
            value = convert_string(split_raw_argument[1])
            
            # Now we add this keyword arg to the keyword_arguments object.
            keyword_arguments[key] = value
        else:
            arguments.append(convert_string(raw_argument))
    
    if not arguments:
        # For clean python, if arguments is empty make it None
        
        arguments = None
    if not keyword_arguments:
        # Same as above.
        
        keyword_arguments = None
    
    return (arguments, keyword_arguments,)

def run():
    '''Run the module.'''
    
    # Parse the args.
    arguments, keyword_arguments = parse_arguments()
    
    if arguments is not None:
        test_module_fullfilename = arguments[0]
    elif keyword_arguments is None:
        # There are zero arguments given, for both keyword and standard arg.
        
        # Raise an exception.
        raise NoArgumentsGiven()
    elif keyword_arguments.has_key('filename'):
        test_module_fullfilename = keyword_arguments['filename']
    else:
        # There are aguments given, but no filename.
        
        # Raise an exception.
        raise NoTestfileGiven()
    
    # Parse the filename into dirname and filename
    test_module_path, test_module_filename = os.path.split(
        test_module_fullfilename)
    
    if keyword_arguments.has_key('entry_function'):
        entry_function = keyword_arguments['entry_function']
    elif keyword_arguments.has_key('ef'):
        entry_function = keyword_arguments['ef']
    else:
        entry_function = None
    
    if not os.path.exists(test_module_fullfilename):
        raise TestfileDoesNotExist()
    
    # Append the path to the sys lib.
    sys.path.append(test_module_path)
    
    def import_test_module():
        test_module = __import__(test_module_filename.split('.')[0])
        if entry_function is not None:
            getattr(test_module, entry_function)()
    
    prof = profile.Profile()
    prof = prof.runctx('import_test_module()', globals(), locals())
    
    # Reroute stdout to modo. And incase the script being tested, decides
    # to reroute stdout, we re-reroute it.. wait.. what?
    sys.stdout = ModoPrinter()
    stats = pstats.Stats(prof)
    stats.sort_stats('cumulative')
    stats.print_stats()
    
    sys.stdout.write_queue()

class mProfileException(exceptions.Exception):
    '''The base mProfile Exception.'''
    pass

class TestfileDoesNotExist(mProfileException):
    ''''''
    pass

class NoArgumentsGiven(mProfileException):
    ''''''
    pass

class NoTestfileGiven(mProfileException):
    ''''''
    pass

class ModoPrinter(object):
    '''The purpose of this class is to be given to sys.stdout so that standard
    prints will be given to modo's event logger.
    
    This is also copied from Moopy, and modified.
    '''
    total_queue = ''
    
    def write(self, content_to_write):
        '''This has been modified to not output anything, but queue.
        '''
        self.total_queue += content_to_write
    
    def write_queue(self):
        ''''''
        
        lx.out(self.total_queue)
        

if __name__ == '__main__':
    run()
