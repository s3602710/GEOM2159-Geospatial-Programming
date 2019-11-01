#set the file path
filepath = ('C:/Users/filal/Documents/2019/Geospatial Programming/Project/Shapefiles/')
#set the tree shapefile name as a variable
Trees = 'Trees_reduced.shp'
#set the area of interest/ construction areas shapefile name as a variable
AOI = 'AOI.shp' 
#set the tree buffer name as a variable 
Tree_Buffer = 'Tree_Buffer.shp'
#set the tree selection extension name as a variable
TPZ_selec = 'TPZ_selec.shp'
#add the tree shapefiles and AOI layers to the interface. 
Tree_Layer = iface.addVectorLayer(filepath + Trees, Trees[:-4], "ogr")
#Add the area of interest layer to the interface. 
AOI_Layer = iface.addVectorLayer(filepath + AOI, AOI[:-4], "ogr")

#start editing the tree points layer. 
Tree_Layer.startEditing()
#add an attribute to the tree points layer for the TPZ calculation.
Tree_Layer.dataProvider().addAttributes([QgsField("TPZ", QVariant.Double)])
#update the new attribute changes. 
Tree_Layer.updateFields()
#commit the changes to the file. 
Tree_Layer.commitChanges()

#Access the features from the tree points layer.    
treeFeatures = Tree_Layer.getFeatures()
#start of the for loop for updating the TPZ valyes. 
for value in treeFeatures:
    #set the equation for the TPZ calculation as a variable
    TPZcalc = (value['Diameter B'] *12)/100
    #start editing the tree points layer.
    Tree_Layer.startEditing()
    #set the values of the TPZ column to that of the TPZ calculation.
    value['TPZ'] = TPZcalc
    #update the values within the attribute.
    Tree_Layer.updateFeature(value)
#commit the changes to the layer.  
Tree_Layer.commitChanges()

#create variable buffers for the tree protection zones. 
buffer= processing.run('native:buffer',{'INPUT': filepath + Trees,
    'DISTANCE': QgsProperty.fromExpression('"TPZ"'),'SEGMENTS':5,'END_CAP_STYLE':0,'JOIN_STYLE':0,'MITER_LIMIT':2,'DISSOLVE':0,'OUTPUT':filepath + Tree_Buffer})
#Add the buffer layer to the interface. 
buff_layer = iface.addVectorLayer(filepath + Tree_Buffer, Tree_Buffer[:-4], "ogr")

#select the buffers that intersect with the construction area/AOI. 
#for loops for the buffer and AOI layers.
for buffer in buff_layer.getFeatures():
    for feat in AOI_Layer.getFeatures():
        #test the intersection of the layers
        if feat.geometry().intersects(buffer.geometry()):
            #if any features of these two layers intersect, select them. 
            buff_layer.select(buffer.id())

#set the active layer as a variable    
TPZ_selection = iface.activeLayer()
#write the selected features from the active layer to file and save as a .shp. 
QgsVectorFileWriter.writeAsVectorFormat(TPZ_selection, filepath + TPZ_selec, "utf-8", TPZ_selection.crs(), "ESRI Shapefile", 1)
#add the selected intersecting features layer to the interface. 
TPZ_Layer = iface.addVectorLayer(filepath + TPZ_selec, TPZ_selec[:-4], "ogr")