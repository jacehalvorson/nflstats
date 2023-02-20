import requests
from bs4 import BeautifulSoup
import csv

# CONSTANTS
# ----------------------------------------------------------------
TXT = 0
CSV = 1
XLSB = 2

MAX_NAME_LENGTH = 15
# ----------------------------------------------------------------

# Global variables
# ----------------------------------------------------------------
htmlObject = None

BASE_URL = 'https://www.nfl.com/stats/player-stats/category/'
QBS_URL = 'https://www.nfl.com/stats/player-stats/'
fumbles2018_url = 'https://www.nfl.com/stats/player-stats/category/fumbles/2018/post/all/defensiveforcedfumble/desc'
# url = 'https://www.nfl.com/stats/player-stats/category/passing/2022/REG/all/passingyards/DESC?aftercursor=AAAAGQAAABlAooAAAAAAADEAlQAQgIhBb1JRbEFFL0JUTXlNREEwWkRVMUxUVXlOamN0TURReE15MDRaRE0yTFdFMVl6Tm1aRGM0TVdGaE1GWitQeFpiSWpJd01qSWlMQ0pTUlVjaUxDSXpNakF3TkdRMU5TMDFNalkzTFRBME1UTXRPR1F6TmkxaE5XTXpabVEzT0RGaFlUQWlYUT09APB____m8H___-ZInE-gq8Tjy5XTH6-5lDzOAAQ='
# ----------------------------------------------------------------


# GET DATA FROM NEXT PAGE
# ----------------------------------------------------------------
def getNextPage( isTableRequested ):
   global htmlObject
   
   if htmlObject == None:
      # If there is no table loaded, return error
      print( 'getNextPage called with no current page' )
      return None
   
   # Find the link of the 'Next Page' button
   footer = htmlObject.find( 'footer', 'd3-o-table__footer')
   if footer == None:
      return None
   url = footer.find_next( 'link' )[ 'href' ]
   if url == None:
      return None
   
   if isTableRequested == True:
      # Return the table found by this url
      return getPageFromURL( url )
   else:
      return url

# Appends the rows of the second table to the first table
def extendTableWithoutFirstRow( firstTable, secondTable ):
   for rowIndex, row in enumerate( secondTable ):
      if rowIndex != 0:
         firstTable.append( row )
      
   return firstTable
# ----------------------------------------------------------------

# SEND GET REQUEST FOR RAW DATA DOWNLOAD AND PARSING
# ----------------------------------------------------------------
def getStringFromURL( url ):
   return formatString( getTableFromURL( url ) )

def getTableFromURL( url ):
   table = getPageFromURL( url )
   
   # Add on stats from all pages
   nextPageTable = getNextPage( True )
   while nextPageTable != None:
      if float( nextPageTable[ 1 ][ 1 ] ) > 0:
         table = extendTableWithoutFirstRow( table, nextPageTable )
         nextPageTable = getNextPage( True )
      else:
         # Unnecessary stats where the first row has 0
         break
   
   return table
   
def getPageFromURL( url ):
   # Retrieve data
   response = requests.get( url )
   
   global htmlObject
   htmlObject = BeautifulSoup( response.text, 'html.parser' )

   # Find the outer table
   table = htmlObject.find( 'table', 'd3-o-table' )

   # Extract the headers and stats
   headers = table.find_next( 'thead' )
   stats = table.find_next( 'tbody' )

   pageTable = [ [ ] ]
   for i, header in enumerate( headers.select( '.header' ) ):
      pageTable[ 0 ].append( header.text )

   # Get a list of players (name + stats)
   players = stats.select( 'tr ')

   for i, player in enumerate( players ):
      # Add a new row for this player's stats
      pageTable.append( [ ] )
      
      # Add each stat to the new row
      for index, stat in enumerate( player.find_all( 'td' ) ):
         pageTable[ i+1 ].append( stat.text )

   return pageTable
# ----------------------------------------------------------------
      
# FORMATTING
# ----------------------------------------------------------------
def formatString( statMatrix ):
   if statMatrix == None:
      print( 'None' )
      return None
   
   formatString = ''

   for rowIndex, row in enumerate( statMatrix ):
      # Newline if it's not the first line
      formatString = ( formatString ) + '\n' if rowIndex > 0 else formatString
      
      for col, cell in enumerate( row ):
         if col == 0 and rowIndex == 1:
            # Add space between titles and stats
            formatString += '\n'
            
         if col == 0 and rowIndex != 0:
            # Player names come with a preceding space so remove it
            cellString = str( cell )[ 1: ]
         else:
            cellString = str( cell )
            
         if col == 14:
            # Only display 13 attributes
            break
         
         if col == 0 and len( cellString ) < MAX_NAME_LENGTH:
            succeedingWhitespace = ( ' ' * ( MAX_NAME_LENGTH - len( cellString ) ) ) + '\t'
         else:
            succeedingWhitespace = '\t'
            
         formatString += ( cellString + succeedingWhitespace )
      
   return formatString
# ----------------------------------------------------------------


# FILE WRITING
# ----------------------------------------------------------------
def writeToFile( fileType, string ):
   if fileType == TXT:
      with open( 'stats.txt', 'w' ) as file:
         file.write( string )
         file.write( '\n' )
         file.close( )
   elif fileType == CSV:
      print( 'Not yet implemented' )
   elif fileType == XLSB:
      print( 'Not yet implemented' )
   else:
      print( f'Invalid file type {fileType}' )
# ----------------------------------------------------------------