import pandas as pd
from typing import Dict, List, Any, Set


class ConfigurationGenerator:
    def __init__(self, df: pd.DataFrame):
        self.df = df
        
    def generate(self, package_name: str) -> Dict[str, Any]:
        """
        Generate Configuration JSON payload from Excel data.
        Builds a nested tree structure based on delimiter-separated commerceVariableName.
        
        Args:
            package_name: The name of the migration package
        """
        configuration_root = {
            "name": "Configuration",
            "category": "CONFIGURATION",
            "children": []
        }
        
        tree = self._build_tree()
        configuration_root["children"] = tree
        
        return {
            "name": package_name,
            "contents": {
                "items": [configuration_root]
            }
        }
    
    def _build_tree(self) -> List[Dict[str, Any]]:
        """
        Build the nested tree structure from Configuration rows.
        """
        # Group data by path
        path_data = {}
        
        for _, row in self.df.iterrows():
            commerce_var = str(row['commerceVariableName'])
            transaction_var = str(row['transactionVariableName'])
            child_var = str(row['childVariableName'])
            child_resource = str(row['childResourceType'])
            granular = bool(row.get('granular', True))
            
            path_segments = commerce_var.split('.')
            
            # Store path information
            if commerce_var not in path_data:
                path_data[commerce_var] = {
                    'segments': path_segments,
                    'transaction_type': transaction_var,
                    'granular': granular,
                    'children': []
                }
            
            # Add unique children only
            child_key = f"{child_var}_{child_resource}"
            existing_children = [f"{c['variableName']}_{c['resourceType']}" 
                                for c in path_data[commerce_var]['children']]
            
            if child_key not in existing_children:
                path_data[commerce_var]['children'].append({
                    'name': child_var,
                    'variableName': child_var,
                    'resourceType': child_resource
                })
        
        # Build the tree structure
        return self._construct_hierarchy(path_data)
    
    def _construct_hierarchy(self, path_data: Dict) -> List[Dict[str, Any]]:
        """
        Construct the hierarchical tree structure with proper nesting.
        """
        # Find the top-level product_family (first segment of all paths)
        top_level_nodes = {}
        
        for path, data in path_data.items():
            segments = data['segments']
            if len(segments) > 0:
                top_segment = segments[0]
                if top_segment not in top_level_nodes:
                    top_level_nodes[top_segment] = {
                        'variableName': top_segment,
                        'name': top_segment.capitalize(),
                        'resourceType': 'product_family',
                        'granular': data['granular']
                    }
        
        # Build complete structure for each top-level node
        result = []
        for top_var, top_node in top_level_nodes.items():
            # Add All Product Family wrapper with duplicated top-level inside
            all_product_family = {
                'name': 'All Product Family',
                'variableName': 'All Product Family',
                'resourceType': 'all_product_family',
                'granular': True,
                'children': []
            }
            
            # Create duplicate of top-level node to go inside All Product Family
            inner_top_node = {
                'name': top_node['name'],
                'variableName': top_node['variableName'],
                'resourceType': 'product_family',
                'granular': top_node['granular'],
                'children': []
            }
            
            # Build children for the inner top node
            inner_children = self._build_children_for_segment(top_var, path_data)
            if inner_children:
                inner_top_node['children'] = inner_children
            
            all_product_family['children'] = [inner_top_node]
            top_node['children'] = [all_product_family]
            
            result.append(top_node)
        
        return result
    
    def _build_children_for_segment(self, parent_var: str, path_data: Dict) -> List[Dict[str, Any]]:
        """
        Build children for a given parent segment.
        """
        children_dict = {}
        
        for path, data in path_data.items():
            segments = data['segments']
            
            # Check if this path starts with parent_var
            if len(segments) > 0 and segments[0] == parent_var:
                if len(segments) > 1:
                    # Process next level
                    next_segment = segments[1]
                    full_path = '.'.join(segments[:2])
                    
                    if next_segment not in children_dict:
                        # Determine resourceType based on depth and transaction_var
                        resource_type = self._get_resource_type(segments, 1, data['transaction_type'])
                        
                        children_dict[next_segment] = {
                            'name': next_segment.capitalize(),
                            'variableName': next_segment,
                            'resourceType': resource_type,
                            'granular': data['granular'],
                            '_children': [],
                            '_leaf_children': []
                        }
                    
                    # Add deeper children or leaf children
                    if len(segments) > 2:
                        # Has more nesting
                        next_path = '.'.join(segments[1:])
                        deeper_children = self._build_children_for_segment(next_segment, 
                                                                           {next_path: {
                                                                               'segments': segments[1:],
                                                                               'transaction_type': data['transaction_type'],
                                                                               'granular': data['granular'],
                                                                               'children': data['children']
                                                                           }})
                        children_dict[next_segment]['_children'].extend(deeper_children)
                    elif path == full_path:
                        # This is the target path, add leaf children
                        children_dict[next_segment]['_leaf_children'].extend(data['children'])
                elif len(segments) == 1 and segments[0] == parent_var:
                    # Leaf children at this level
                    if '_direct_children' not in children_dict:
                        children_dict['_direct_children'] = []
                    children_dict['_direct_children'].extend(data['children'])
        
        # Convert to list and merge children
        result = []
        for key, node in children_dict.items():
            if key == '_direct_children':
                result.extend(node)
            else:
                node_obj = {
                    'name': node['name'],
                    'variableName': node['variableName'],
                    'resourceType': node['resourceType'],
                    'granular': node['granular']
                }
                
                all_children = node['_children'] + node['_leaf_children']
                if all_children:
                    node_obj['children'] = all_children
                
                result.append(node_obj)
        
        return result
    
    def _get_resource_type(self, segments: List[str], depth: int, transaction_type: str) -> str:
        """
        Determine resource type based on depth and transaction type.
        """
        type_hierarchy = ['product_family', 'product_line', 'model']
        
        # If this is the last segment, use transaction_type
        if depth == len(segments) - 1:
            return transaction_type
        
        # Otherwise, work backwards from transaction_type
        if transaction_type in type_hierarchy:
            trans_index = type_hierarchy.index(transaction_type)
            levels_from_end = len(segments) - 1 - depth
            target_index = trans_index - levels_from_end
            return type_hierarchy[max(0, target_index)]
        
        return 'product_family'
