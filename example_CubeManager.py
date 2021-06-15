######################################################################################################
# DESCRIPTION OF THIS SCRIPT:
# Basic script to learn how to use the 'CubeManager' class from 'hsi_dataManager.py' file.
#-----------------------------------------------------------------------------------------------------
# It demonstrates:
#   1) How to create a CubeManager instance
#   2) How to load '_dataset.mat' files to the CubeManager instance for training
#   3) How to create 2D batches with loaded data in the CubeManager instance
#   4) How to convert 2D batches to batch PyTorch tensors with the CubeManager instance
#   5) How to create a FourLayerNet model and how to train it with the batch 
#   6) How to load a single '_dataset.mat' with a new CubeManager instance for testing
#   7) How to predict the test dataset with our trained model
#   8) How to compute prediction metrics and print them
#######################################################################################################

import torch                        # Import PyTorch

import hsi_dataManager as hsi_dm    # Import 'hsi_dataManager.py' file as 'hsi_dm' to load use all desired functions 
import nn_models as models          # Import 'nn_models.py' file as 'models' to define any new Neural Network included in the file 
import metrics as mts               # Import 'metrics.py' file as 'mts' to evluate metrics
import numpy as np                  # Import Numpy as np

#*#############################
#*#### START MAIN PROGRAM #####
#*

# Desired patient images ID
# ['ID0018C09', 'ID0025C02', 'ID0029C02', 'ID0030C02', 'ID0033C02', 'ID0034C02', 'ID0035C02', 'ID0038C02', 'ID0047C02', 'ID0047C08', 'ID0050C05', 'ID0051C05', 'ID0056C02', 'ID0064C04',
# 'ID0064C06', 'ID0065C01', 'ID0065C09', 'ID0067C01', 'ID0068C08', 'ID0070C02', 'ID0070C05', 'ID0070C08', 'ID0071C02', 'ID0071C011', 'ID0071C014']
patients_list_train = ['ID0018C09', 'ID0025C02', 'ID0029C02']
patient_test = ['ID0029C02']

# Directories with data
dir_datasets = "NEMESIS_images/datasets/"
dir_gtMaps = "NEMESIS_images/GroundTruthMaps/"
dir_preProImages = "NEMESIS_images/preProcessedImages/"
dir_rawImages = "NEMESIS_images/tif/"

# Python dictionary to convert labels to label4Classes
dic_label = {'101': 1, '200': 2, '220': 2, '221': 2, '301': 3, '302': 4, '320': 5, '331': 6}

# Determine dimension of batches for the Neural Network
batch_dim = '2D'

#*####################
#* LOAD TRAIN IMAGES
print("\n##########")
print("Loading training images. Please wait...")

# Create an instance of 'CubeManager'
cm_train = hsi_dm.CubeManager(patch_size = 7, batch_size = 64, dic_label = dic_label, batch_dim = batch_dim)

# Load all desired pixels to the 'CubeManager' instance 'cm_train' (all data is stored inside the instance attributes)
cm_train.load_patient_cubes(patients_list_train, dir_gtMaps, dir_preProImages)

print("\tTraining images have been loaded. Creating training batches...")

# Create batches with the loaded data. Returns 'batches' which is a Python dictionary including 2 Python lists, 'data' and 'labels', containing all batches
batches_train = cm_train.create_batches()

"""
# PRINT IN TERMINAL THE SHAPE OF EVERY CREATED BATCH
i = 0
for b in batches_train['cube']:
    print('Size of batch ', i+1, ' = ', batches_train['cube'][i].shape )
    i += 1

print('Last batch ', batches_train['cube'][i-1] )
"""

print("\tTraining batches have been created. Converting data and label batches to tensors...")

if ( batch_dim == '2D' ):
    # Convert 'data' and 'label4Classes' batches to PyTorch tensors for training our Neural Network
    data_tensor_batch = cm_train.batch_to_tensor(batches_train['data'], data_type = torch.float)
    labels_tensor_batch = cm_train.batch_to_tensor(batches_train['label4Classes'], data_type = torch.LongTensor)

elif ( batch_dim == '3D' ):
    # Convert 'cube' and 'label' batches to PyTorch tensors for training our Neural Network
    data_tensor_batch = cm_train.batch_to_tensor(batches_train['cube'], data_type = torch.float)
    labels_tensor_batch = cm_train.batch_to_tensor(batches_train['label'], data_type = torch.LongTensor)

    print('### DEBUG ###')
    print('data_tensor_batch[0].shape = ', data_tensor_batch[0].shape)
    stop


print("\tTensors have been created.")



#*######################
#* TRAIN NEURAL NETWORK
print("\n##########")
print("Training your Neural Network. Please wait...")

if ( batch_dim == '2D' ):
    # Create a FourLayerNet model, which contains 4 fully connected layers with relu activation functions
    model = models.FourLayerNet(D_in = cm_train.data.shape[-1], H = 16, D_out = cm_train.numUniqueLabels)

    # Train FourLayerNet model
    model.trainNet(batch_x = data_tensor_batch, batch_y = labels_tensor_batch, epochs = 10, plot = True, lr = 0.01)

elif ( batch_dim == '3D' ):
    print('First train your 3D CNN! :)')
    stop


#*###################
#* LOAD TEST IMAGES
print("\n##########")
print("Loading test image. Please wait...")

# Create an instance of 'CubeManager'
cm_test = hsi_dm.CubeManager(patch_size = 7, batch_size = 64, dic_label = dic_label, batch_dim = batch_dim)

# Load all desired pixels to the 'CubeManager' instance 'cm_test' (all data is stored inside the instance attributes)
cm_test.load_patient_cubes(patients_list = patient_test, dir_path_gt = dir_gtMaps, dir_par_preProcessed = dir_preProImages)

print("\tTest image has been loaded. Creating test batches...")

# Create batches with the loaded data. Returns 'batches' which is a Python dictionary including 2 Python lists, 'data' and 'labels', containing all batches
batches_test = cm_test.create_batches()

print("\tTest batches have been created. Converting data batches to tensors...")

if ( batch_dim == '2D' ):
    # Convert 'data' batches to PyTorch tensors for training our Neural Network
    data_tensor_batch_test = cm_test.batch_to_tensor(batches_test['data'], data_type = torch.float)
elif ( batch_dim == '3D' ):
    # Convert 'cube' batches to PyTorch tensors for training our Neural Network
    data_tensor_batch_test = cm_test.batch_to_tensor(batches_test['cube'], data_type = torch.float)

print("\tTensors have been created.")

#*##############################################
#* PREDICT TEST IMAGES WITH OUT NEURAL NETWORK
print("\n##########")
print("Predict loaded test images with trained model.")
print("\nModel predicting patient image = ", cm_test.patients_list[0] )

if ( batch_dim == '2D' ):
    # Predict with the FourLayerNet model
    pred_labels = model.predict(batch_x = data_tensor_batch_test)
if ( batch_dim == '3D' ):
    print('First train your 3D CNN! :)')
    stop

#*##############################################
#* COMPUTE METRICS WITH THE MODEL PREDICTION

# Evaluate how well the model can predict a new image unused during training
# batches['label4Classes']: is a Python list where each element contains the labels for each of the samples in the corresponding batch
# by calling the 'batch_to_label_vector()' method, we generate a column numpy array from the Python list and store all batches labels in order
# pred_labels: is a numpy column vector with all predicted labels of all batches in order
metrics = mts.get_metrics(cm_test.batch_to_label_vector(batches_test['label4Classes']), pred_labels, cm_test.numUniqueLabels)

print("\nMetrics after predicting:")
print('\tOACC = ', str(metrics['OACC']))
print('\tACC = ', str(metrics['ACC']))
print('\tSEN = ', str(metrics['SEN']))
print('\tSPE = ', str(metrics['SPE']))
print('\tPRECISION = ', str(metrics['PRECISION']))
print('\tCONFUSION MATRIX: \n\t', str(metrics['CON_MAT']))

#*###############################
#* COMPUTE CLASSIFICATION MAP

print("\n##########")
print("Plotting classification maps")

# To compute classification maps, it is necessary to have used the 'CubeManager' class, since it
# provides the X and Y coordenates for every pixel in every predicted batch.
# Please note that 'DataManager' class does no provide the coordenates to any sample.

# Concatenate all list elements from 'batches_test['label4Classes']' (all label batches) to a numpy array
true_labels = cm_test.concatenate_list_to_numpy(batches_test['label4Classes'])
# Do the same with the coordenates to know the predicted label and its corresponding position
label_coordenates = cm_test.concatenate_list_to_numpy(batches_test['label_coords']).astype(int)

# Extract dimension of the loaded groundTruthMap for the test patient
dims = cm_test.patient_cubes[patient_test[0]]['raw_groundTruthMap'].shape

# Generate classification map from the predicted labels
mts.get_classification_map(pred_labels, true_labels, label_coordenates, dims, title="Test classification Map", plot = True, save_plot = False, save_path = None, plot_gt = False)


#*#### END MAIN PROGRAM #####
#*###########################