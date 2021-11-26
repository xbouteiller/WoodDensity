



if __name__=="__main__":
   import pandas
   import wood.wooddensity

   from wood.wooddensity import WoodDensity

   import configparser

   wd = WoodDensity()
   print(wd)

   
   wd.read_file_write_bound()
   wd.label_df()
   
   