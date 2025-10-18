import pandas as pd
from typing import Dict, List, Any


class ConfigurationGenerator:
    def __init__(self, df: pd.DataFrame):
        self.df = df
        
    def generate(self) -> Dict[str, Any]:
        """
        Generate Configuration JSON payload from Excel data.
        Builds a nested tree structure based on delimiter-separated commerceVariableName.
        """
        configuration_root = {
            "name": "Configuration",
            "category": "CONFIGURATION",
            "children": []
        }
        
        tree = self._build_tree()
        
        configuration_root["children"] = tree
        
        return {
            "contents": {
                "items": [configuration_root]
            }
        }
    
    def _build_tree(self) -> List[Dict[str, Any]]:
        """
        Build the nested tree structure from Configuration rows.
        Returns the list of top-level children (product families).
        """
        tree_dict = {}
        
        for _, row in self.df.iterrows():
            commerce_var = str(row['commerceVariableName'])
            transaction_var = str(row['transactionVariableName'])
            child_var = str(row['childVariableName'])
            child_resource = str(row['childResourceType'])
            granular = bool(row.get('granular', True))
            
            path_segments = commerce_var.split('.')
            
            self._insert_into_tree(
                tree_dict, 
                path_segments, 
                transaction_var, 
                child_var, 
                child_resource,
                granular
            )
        
        return self._convert_tree_to_list(tree_dict)
    
    def _insert_into_tree(
        self, 
        tree_dict: Dict, 
        path_segments: List[str], 
        transaction_var: str,
        child_var: str,
        child_resource: str,
        granular: bool
    ):
        """
        Insert a path and its child into the tree dictionary.
        """
        current_level = tree_dict
        
        for i, segment in enumerate(path_segments):
            if segment not in current_level:
                current_level[segment] = {
                    '_info': {
                        'variableName': segment,
                        'name': segment.capitalize(),
                        'granular': granular
                    },
                    '_children': {},
                    '_leaf_children': []
                }
            
            if i == len(path_segments) - 1:
                resource_type = transaction_var
                current_level[segment]['_info']['resourceType'] = resource_type
                
                leaf_child = {
                    'name': child_var,
                    'variableName': child_var,
                    'resourceType': child_resource
                }
                current_level[segment]['_leaf_children'].append(leaf_child)
            else:
                current_level = current_level[segment]['_children']
        
        self._determine_intermediate_resource_types(tree_dict, transaction_var)
    
    def _determine_intermediate_resource_types(self, tree_dict: Dict, deepest_type: str):
        """
        Determine resource types for intermediate nodes based on the deepest level type.
        Hierarchy: product_family > product_line > model
        """
        type_hierarchy = ['product_family', 'product_line', 'model']
        
        if deepest_type not in type_hierarchy:
            return
        
        deepest_index = type_hierarchy.index(deepest_type)
        
        def assign_types(node_dict, depth=0):
            for key, node in node_dict.items():
                if '_info' in node:
                    if 'resourceType' not in node['_info']:
                        index = max(0, deepest_index - depth)
                        node['_info']['resourceType'] = type_hierarchy[index]
                    
                    if node['_children']:
                        assign_types(node['_children'], depth + 1)
        
        assign_types(tree_dict)
    
    def _convert_tree_to_list(self, tree_dict: Dict) -> List[Dict[str, Any]]:
        """
        Convert the tree dictionary to the final nested list structure.
        Adds the "All Product Family" wrapper.
        """
        result = []
        
        for key, node in tree_dict.items():
            node_obj = {
                'name': node['_info']['name'],
                'variableName': node['_info']['variableName'],
                'resourceType': node['_info']['resourceType'],
                'granular': node['_info']['granular']
            }
            
            all_product_family_wrapper = {
                'name': 'All Product Family',
                'variableName': 'All Product Family',
                'resourceType': 'all_product_family',
                'granular': True,
                'children': []
            }
            
            nested_children = self._build_nested_structure(node)
            
            if nested_children:
                all_product_family_wrapper['children'] = nested_children
                node_obj['children'] = [all_product_family_wrapper]
            
            result.append(node_obj)
        
        return result
    
    def _build_nested_structure(self, node: Dict) -> List[Dict[str, Any]]:
        """
        Recursively build the nested children structure.
        """
        children = []
        
        for key, child_node in node['_children'].items():
            child_obj = {
                'name': child_node['_info']['name'],
                'variableName': child_node['_info']['variableName'],
                'resourceType': child_node['_info']['resourceType'],
                'granular': child_node['_info']['granular']
            }
            
            nested_children = self._build_nested_structure(child_node)
            leaf_children = child_node['_leaf_children']
            
            all_children = nested_children + leaf_children
            
            if all_children:
                child_obj['children'] = all_children
            
            children.append(child_obj)
        
        children.extend(node['_leaf_children'])
        
        return children
