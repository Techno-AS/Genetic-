#!/usr/bin/env python
# coding: utf-8

# In[49]:


import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import math
import random
import statistics
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import cross_val_score

data = pd.read_csv('data.csv')

data.head()


# In[50]:


data.shape


# In[51]:


data.diagnosis.value_counts()

data.isna().any()

data.drop(['id','Unnamed: 32'],axis=1,inplace=True)

data.shape


# In[52]:


y = data['diagnosis']
x = data.drop('diagnosis',axis =1)

y.replace(to_replace='M',value= 1,inplace=True)
y.replace(to_replace='B',value = 0,inplace=True)


# In[53]:


data


# In[66]:


"""# Genetic Algorithm Code"""



def genetic_algo(data,features,target,population_size,tol_level,top_number):

     def init_population(population_size,c,top_number):
        population = []
        for i in range(population_size):
            individual = [0]*c
            j = 0
            while(j<top_number):
                p = random.uniform(0,1)
                position = random.randrange(c)
                if(p>=0.5 and individual[position]==0):
                    individual[position]=1
                    j=j+1

      #edge case if all genes are 0 then we will make any one gene as 1
            if(sum(individual)==0):
                position = random.randrange(c)
                individual[position] = 1
            population.append(individual)
            print('population is ')
            print(population)
            print('------------------')
        return population




     def calculate_fitness(features,target):
        model = RandomForestClassifier()
        scores = cross_val_score(model,features,target,scoring='f1_macro',n_jobs=-1,cv=10) #using f1_score as it is an imbalanced dataset
        print(scores.mean())
        return scores.mean()


  
     def get_fitness(population,data):
        fitness_values = []
        for individual in population:
            df = data
            i=0
            for column in data:
                if(individual[i]==0):
                    df = df.drop(column,axis=1)
                i=i+1

            features = df
            individual_fitness = calculate_fitness(features,target)
            fitness_values.append(individual_fitness)

        return fitness_values



     def select_parents(population,fitness_values):
        parents = []
        total = sum(fitness_values)
        norm_fitness_values = [x/total for x in fitness_values]

    #find cumulative fitness values for roulette wheel selection
        cumulative_fitness = []
        start = 0
        for norm_value in norm_fitness_values:
            start+=norm_value
            cumulative_fitness.append(start)

        population_size = len(population)
        for count in range(population_size):
            random_number = random.uniform(0, 1)
            individual_number = 0
            for score in cumulative_fitness:
                if(random_number<=score):
                    parents.append(population[individual_number])
                    break
                individual_number+=1
        return parents



  #high probability crossover
     def two_point_crossover(parents,probability):
        random.shuffle(parents)
    #count number of pairs for crossover
        no_of_pairs = round(len(parents)*probability/2)
        chromosome_len = len(parents[0])
        crossover_population = []
  
        for num in range(no_of_pairs):
            length = len(parents)
            parent1_index = random.randrange(length)
            parent2_index = random.randrange(length)
            while(parent1_index == parent2_index):
                parent2_index = random.randrange(length)
        
            start = random.randrange(chromosome_len)
            end = random.randrange(chromosome_len)
            if(start>end):
                start,end = end, start

            parent1 = parents[parent1_index]
            parent2 = parents[parent2_index]
            child1 =  parent1[0:start] 
            child1.extend(parent2[start:end])
            child1.extend(parent1[end:])
            child2 =  parent2[0:start]
            child2.extend(parent1[start:end])
            child2.extend(parent2[end:])
            parents.remove(parent1)
            parents.remove(parent2)
            crossover_population.append(child1)
            crossover_population.append(child2)

    #to append remaining parents which are not undergoing crossover process
            if(len(parents)>0):
               for remaining_parents in parents:
                    crossover_population.append(remaining_parents)

            return crossover_population



  #low probability mutation
  #mutation_probability is generally low to avoid a lot of randomness 
        def mutation(crossover_population):
    #swapping of zero with one to retain no of features required
          for individual in crossover_population:
            index_1 = random.randrange(len(individual))
            index_2 = random.randrange(len(individual))
            while(index_2==index_1 and individual[index_1] != individual[index_2]):
                 index_2 = random.randrange(len(individual))

      #swapping the bits
            temp = individual[index_1]
            individual[index_1] = individual[index_2]
            individual[index_2] = temp

        return crossover_population
        c = data.shape[1] #length of the chromosome
        population= init_population(population_size,c,top_number)
        fitness_values = get_fitness(population,data)
        parents = select_parents(population,fitness_values)
        crossover_population = two_point_crossover(parents,0.78)
        population = crossover_population
        p = random.uniform(0,1)
        if(p<=0.001): 
            mutated_population = mutation(crossover_population)
            population = mutated_population
        fitness_values = get_fitness(population,data)
        variance_of_population = statistics.variance(fitness_values)
        print("variance is",variance_of_population)
        gen = 1


  #repeating algorithm til stopping criterion is met
        while(variance_of_population > tol_level):
            print('generation-',gen)
            parents = select_parents(population,fitness_values)
            crossover_population = two_point_crossover(parents,0.78)
            population = crossover_population
            p = random.uniform(0,1)
            if(p<=0.001): #mutation prob here
                mutated_population = mutation(crossover_population)
                population = mutated_population
            fitness_values = get_fitness(population,data)
            variance_of_population = statistics.variance(fitness_values)
            print("variance is",variance_of_population)
            gen+=1

            best_features = []
            best_f1_score = 0
            optimal_fitness = sum(fitness_values)/len(fitness_values)
            print('avg fitness is: ',optimal_fitness)
            for index,fitness_value in enumerate(fitness_values):
                error = abs((fitness_value - optimal_fitness)/optimal_fitness)
            if(error <= 0.01):
                best_features = population[index]
                best_f1_score = fitness_value
            print(best_features)
            return best_features,best_f1_score



# In[67]:


#running the algorithm
top_features, best_f1_score = genetic_algo(x,x,y,40,0.000005,25)

#printing top features selected through genetic algorithm
i = 0
list_of_features= []
for i in range(len(top_features)):
    if(top_features[i]==1):
         list_of_features.append(x.columns[i])

print(top_features)
print(list_of_features)
print(best_f1_score)
         


# In[ ]:




