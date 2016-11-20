import unittest

from prometheus_es_exporter import format_metric_name, format_label_value
from prometheus_es_exporter.parser import parse_response

def format_label(key, value_list):
    return key + '="' + format_label_value(value_list) + '"'

def format_metric(name_list, label_dict):
    name = format_metric_name(name_list)

    if len(label_dict) > 0:
        labels = '{'
        labels += ','.join([format_label(k, v) for k, v in label_dict.items()])
        labels += '}'
    else:
        labels = ''

    return name + labels

# Converts the parse_response() result into a psuedo-prometheus format
# that is useful for comparing results in tests.
def convert_result(result):
    return {
        format_metric(name_list, label_dict): value
        for (name_list, label_dict, value) in result
    }

# Sample responses generated by running the provided queries on a Elasticsearch
# server populated with the following data (http command = Httpie utility):
# > http -v POST localhost:9200/foo/bar/1 val:=1 group1=a group2=a
# > http -v POST localhost:9200/foo/bar/2 val:=2 group1=a group2=b
# > http -v POST localhost:9200/foo/bar/3 val:=3 group1=b group2=b
class Test(unittest.TestCase):
    maxDiff = None

    def test_query(self):
        # Query:
        # {
        #     'size': 0,
        #     'query': {
        #         'match_all': {}
        #     }
        # }
        response = {
            "_shards": {
                "failed": 0,
                "successful": 5,
                "total": 5
            },
            "hits": {
                "hits": [],
                "max_score": 0.0,
                "total": 3
            },
            "timed_out": False,
            "took": 1
        }

        expected = {
            'hits': 3
        }
        result = convert_result(parse_response(response))
        self.assertEqual(result, expected)

    # effectively tests other singe-value metrics: max,min,sum,cardinality
    def test_avg(self):
        # Query:
        # {
        #     'size': 0,
        #     'query': {
        #         'match_all': {}
        #     },
        #     'aggs': {
        #         'val_avg': {
        #             'avg': {'field': 'val'}
        #         }
        #     }
        # }
        response = {
            "_shards": {
                "failed": 0,
                "successful": 5,
                "total": 5
            },
            "aggregations": {
                "val_avg": {
                    "value": 2.0
                }
            },
            "hits": {
                "hits": [],
                "max_score": 0.0,
                "total": 3
            },
            "timed_out": False,
            "took": 1
        }

        expected = {
            'hits': 3,
            'val_avg_value': 2
        }
        result = convert_result(parse_response(response))
        self.assertEqual(result, expected)

    # effecively tests other mult-value metrics: percentile_ranks
    def test_percentiles(self):
        # Query:
        # {
        #     'size': 0,
        #     'query': {
        #         'match_all': {}
        #     },
        #     'aggs': {
        #         'val_percentiles': {
        #             'percentiles': {'field': 'val'}
        #         }
        #     }
        # }
        response = {
            "_shards": {
                "failed": 0,
                "successful": 5,
                "total": 5
            },
            "aggregations": {
                "val_percentiles": {
                    "values": {
                        "1.0": 1.02,
                        "25.0": 1.5,
                        "5.0": 1.1,
                        "50.0": 2.0,
                        "75.0": 2.5,
                        "95.0": 2.9,
                        "99.0": 2.98
                    }
                }
            },
            "hits": {
                "hits": [],
                "max_score": 0.0,
                "total": 3
            },
            "timed_out": False,
            "took": 1
        }

        expected = {
            'hits': 3,
            'val_percentiles_values_1_0': 1.02,
            'val_percentiles_values_5_0': 1.1,
            'val_percentiles_values_25_0': 1.5,
            'val_percentiles_values_50_0': 2.0,
            'val_percentiles_values_75_0': 2.5,
            'val_percentiles_values_95_0': 2.9,
            'val_percentiles_values_99_0': 2.98
        }
        result = convert_result(parse_response(response))
        self.assertEqual(result, expected)

    def test_stats(self):
        # Query:
        # {
        #     'size': 0,
        #     'query': {
        #         'match_all': {}
        #     },
        #     'aggs': {
        #         'val_stats': {
        #             'stats': {'field': 'val'}
        #         }
        #     }
        # }
        response = {
            "_shards": {
                "failed": 0,
                "successful": 5,
                "total": 5
            },
            "aggregations": {
                "val_stats": {
                    "avg": 2.0,
                    "count": 3,
                    "max": 3.0,
                    "min": 1.0,
                    "sum": 6.0
                }
            },
            "hits": {
                "hits": [],
                "max_score": 0.0,
                "total": 3
            },
            "timed_out": False,
            "took": 1
        }

        expected = {
            'hits': 3,
            'val_stats_avg': 2.0,
            'val_stats_count': 3,
            'val_stats_max': 3.0,
            'val_stats_min': 1.0,
            'val_stats_sum': 6.0
        }
        result = convert_result(parse_response(response))
        self.assertEqual(result, expected)

    def test_extended_stats(self):
        # Query:
        # {
        #     'size': 0,
        #     'query': {
        #         'match_all': {}
        #     },
        #     'aggs': {
        #         'val_extended_stats': {
        #             'extended_stats': {'field': 'val'}
        #         }
        #     }
        # }
        response = {
            "_shards": {
                "failed": 0,
                "successful": 5,
                "total": 5
            },
            "aggregations": {
                "val_extended_stats": {
                    "avg": 2.0,
                    "count": 3,
                    "max": 3.0,
                    "min": 1.0,
                    "std_deviation": 0.816496580927726,
                    "std_deviation_bounds": {
                        "lower": 0.36700683814454793,
                        "upper": 3.632993161855452
                    },
                    "sum": 6.0,
                    "sum_of_squares": 14.0,
                    "variance": 0.6666666666666666
                }
            },
            "hits": {
                "hits": [],
                "max_score": 0.0,
                "total": 3
            },
            "timed_out": False,
            "took": 1
        }

        expected = {
            'hits': 3,
            'val_extended_stats_avg': 2.0,
            'val_extended_stats_count': 3,
            'val_extended_stats_max': 3.0,
            'val_extended_stats_min': 1.0,
            'val_extended_stats_sum': 6.0,
            'val_extended_stats_std_deviation': 0.816496580927726,
            'val_extended_stats_std_deviation_bounds_lower': 0.36700683814454793,
            'val_extended_stats_std_deviation_bounds_upper': 3.632993161855452,
            'val_extended_stats_sum_of_squares': 14.0,
            'val_extended_stats_variance': 0.6666666666666666

        }
        result = convert_result(parse_response(response))
        self.assertEqual(result, expected)

    def test_filter(self):
        # Query:
        # {
        #     'size': 0,
        #     'query': {
        #         'match_all': {}
        #     },
        #     'aggs': {
        #         'group1_filter': {
        #             'filter': {'term': {'group1': 'a'}},
        #             'aggs': {
        #                 'val_sum': {
        #                     'sum': {'field': 'val'}
        #                 }
        #             }
        #         }
        #     }
        # }
        response = {
            "_shards": {
                "failed": 0,
                "successful": 5,
                "total": 5
            },
            "aggregations": {
                "group1_filter": {
                    "doc_count": 2,
                    "val_sum": {
                        "value": 3.0
                    }
                }
            },
            "hits": {
                "hits": [],
                "max_score": 0.0,
                "total": 3
            },
            "timed_out": False,
            "took": 1
        }

        expected = {
            'hits': 3,
            'group1_filter_doc_count': 2,
            'group1_filter_val_sum_value': 3.0
        }
        result = convert_result(parse_response(response))
        self.assertEqual(result, expected)

    def test_filters(self):
        # Query:
        # {
        #     'size': 0,
        #     'query': {
        #         'match_all': {}
        #     },
        #     'aggs': {
        #         'group_filters': {
        #             'filters': {
        #                 'filters': {
        #                     'group_a': {'term': {'group1': 'a'}},
        #                     'group_b': {'term': {'group1': 'b'}}
        #                 }
        #             },
        #             'aggs': {
        #                 'val_sum': {
        #                     'sum': {'field': 'val'}
        #                 }
        #             }
        #         }
        #     }
        # }
        response = {
            "_shards": {
                "failed": 0,
                "successful": 5,
                "total": 5
            },
            "aggregations": {
                "group_filters": {
                    "buckets": {
                        "group_a": {
                            "doc_count": 2,
                            "val_sum": {
                                "value": 3.0
                            }
                        },
                        "group_b": {
                            "doc_count": 1,
                            "val_sum": {
                                "value": 3.0
                            }
                        }
                    }
                }
            },
            "hits": {
                "hits": [],
                "max_score": 0.0,
                "total": 3
            },
            "timed_out": False,
            "took": 1
        }

        expected = {
            'hits': 3,
            'group_filters_doc_count{group_filters="group_a"}': 2,
            'group_filters_doc_count{group_filters="group_b"}': 1,
            'group_filters_val_sum_value{group_filters="group_a"}': 3.0,
            'group_filters_val_sum_value{group_filters="group_b"}': 3.0
        }
        result = convert_result(parse_response(response))
        self.assertEqual(result, expected)

    def test_filters_anonymous(self):
        # Query:
        # {
        #     'size': 0,
        #     'query': {
        #         'match_all': {}
        #     },
        #     'aggs': {
        #         'group_filters': {
        #             'filters': {
        #                 'filters': [
        #                     {'term': {'group1': 'a'}},
        #                     {'term': {'group1': 'b'}}
        #                 ]
        #             },
        #             'aggs': {
        #                 'val_sum': {
        #                     'sum': {'field': 'val'}
        #                 }
        #             }
        #         }
        #     }
        # }
        response = {
            "_shards": {
                "failed": 0,
                "successful": 5,
                "total": 5
            },
            "aggregations": {
                "group_filters": {
                    "buckets": [
                        {
                            "doc_count": 2,
                            "val_sum": {
                                "value": 3.0
                            }
                        },
                        {
                            "doc_count": 1,
                            "val_sum": {
                                "value": 3.0
                            }
                        }
                    ]
                }
            },
            "hits": {
                "hits": [],
                "max_score": 0.0,
                "total": 3
            },
            "timed_out": False,
            "took": 1
        }

        expected = {
            'hits': 3,
            'group_filters_doc_count{group_filters="filter_0"}': 2,
            'group_filters_doc_count{group_filters="filter_1"}': 1,
            'group_filters_val_sum_value{group_filters="filter_0"}': 3.0,
            'group_filters_val_sum_value{group_filters="filter_1"}': 3.0
        }
        result = convert_result(parse_response(response))
        self.assertEqual(result, expected)

    def test_terms(self):
        # Query:
        # {
        #     'size': 0,
        #     'query': {
        #         'match_all': {}
        #     },
        #     'aggs': {
        #         'group1_terms': {
        #             'terms': {'field': 'group1'},
        #             'aggs': {
        #                 'val_sum': {
        #                     'sum': {'field': 'val'}
        #                 }
        #             }
        #         }
        #     }
        # }
        response = {
            "_shards": {
                "failed": 0,
                "successful": 5,
                "total": 5
            },
            "aggregations": {
                "group1_terms": {
                    "buckets": [
                        {
                            "doc_count": 2,
                            "key": "a",
                            "val_sum": {
                                "value": 3.0
                            }
                        },
                        {
                            "doc_count": 1,
                            "key": "b",
                            "val_sum": {
                                "value": 3.0
                            }
                        }
                    ],
                    "doc_count_error_upper_bound": 0,
                    "sum_other_doc_count": 0
                }
            },
            "hits": {
                "hits": [],
                "max_score": 0.0,
                "total": 3
            },
            "timed_out": False,
            "took": 2
        }

        expected = {
            'hits': 3,
            'group1_terms_doc_count_error_upper_bound': 0,
            'group1_terms_sum_other_doc_count': 0,
            'group1_terms_doc_count{group1_terms="a"}': 2,
            'group1_terms_val_sum_value{group1_terms="a"}': 3.0,
            'group1_terms_doc_count{group1_terms="b"}': 1,
            'group1_terms_val_sum_value{group1_terms="b"}': 3.0
        }
        result = convert_result(parse_response(response))
        self.assertEqual(result, expected)

    def test_terms_numeric(self):
        # Query:
        # {
        #     'size': 0,
        #     'query': {
        #         'match_all': {}
        #     },
        #     'aggs': {
        #         'val_terms': {
        #             'terms': {'field': 'val'},
        #             'aggs': {
        #                 'val_sum': {
        #                     'sum': {'field': 'val'}
        #                 }
        #             }
        #         }
        #     }
        # }
        response = {
            "_shards" : {
                "total" : 5,
                "successful" : 5,
                "failed" : 0
            },
            "aggregations" : {
                "val_terms" : {
                    "doc_count_error_upper_bound" : 0,
                    "sum_other_doc_count" : 0,
                    "buckets" : [
                        {
                            "key" : 1,
                            "doc_count" : 1,
                            "val_sum" : {
                                "value" : 1.0
                            }
                        },
                        {
                            "key" : 2,
                            "doc_count" : 1,
                            "val_sum" : {
                              "value" : 2.0
                            }
                        },
                        {
                            "key" : 3,
                            "doc_count" : 1,
                            "val_sum" : {
                                "value" : 3.0
                            }
                        }
                    ]
                }
            },
            "hits" : {
                "total" : 3,
                "max_score" : 0.0,
                "hits" : []
            },
            "timed_out" : False,
            "took" : 4
        }


        expected = {
            'hits': 3,
            'val_terms_doc_count_error_upper_bound': 0,
            'val_terms_sum_other_doc_count': 0,
            'val_terms_doc_count{val_terms="1"}': 1,
            'val_terms_val_sum_value{val_terms="1"}': 1.0,
            'val_terms_doc_count{val_terms="2"}': 1,
            'val_terms_val_sum_value{val_terms="2"}': 2.0,
            'val_terms_doc_count{val_terms="3"}': 1,
            'val_terms_val_sum_value{val_terms="3"}': 3.0
        }
        result = convert_result(parse_response(response))
        self.assertEqual(result, expected)

    def test_nested_terms(self):
        # Query:
        # {
        #     'size': 0,
        #     'query': {
        #         'match_all': {}
        #     },
        #     'aggs': {
        #         'group1_terms': {
        #             'terms': {'field': 'group1'},
        #             'aggs': {
        #                 'val_sum': {
        #                     'sum': {'field': 'val'}
        #                 },
        #                 'group2_terms': {
        #                     'terms': {'field': 'group2'},
        #                     'aggs': {
        #                         'val_sum': {
        #                             'sum': {'field': 'val'}
        #                         }
        #                     }
        #                 }
        #             }
        #         }
        #     }
        # }
        response = {
            "_shards": {
                "failed": 0,
                "successful": 5,
                "total": 5
            },
            "aggregations": {
                "group1_terms": {
                    "buckets": [
                        {
                            "doc_count": 2,
                            "group2_terms": {
                                "buckets": [
                                    {
                                        "doc_count": 1,
                                        "key": "a",
                                        "val_sum": {
                                            "value": 1.0
                                        }
                                    },
                                    {
                                        "doc_count": 1,
                                        "key": "b",
                                        "val_sum": {
                                            "value": 2.0
                                        }
                                    }
                                ],
                                "doc_count_error_upper_bound": 0,
                                "sum_other_doc_count": 0
                            },
                            "key": "a",
                            "val_sum": {
                                "value": 3.0
                            }
                        },
                        {
                            "doc_count": 1,
                            "group2_terms": {
                                "buckets": [
                                    {
                                        "doc_count": 1,
                                        "key": "b",
                                        "val_sum": {
                                            "value": 3.0
                                        }
                                    }
                                ],
                                "doc_count_error_upper_bound": 0,
                                "sum_other_doc_count": 0
                            },
                            "key": "b",
                            "val_sum": {
                                "value": 3.0
                            }
                        }
                    ],
                    "doc_count_error_upper_bound": 0,
                    "sum_other_doc_count": 0
                }
            },
            "hits": {
                "hits": [],
                "max_score": 0.0,
                "total": 3
            },
            "timed_out": False,
            "took": 2
        }

        expected = {
            'hits': 3,
            'group1_terms_doc_count_error_upper_bound': 0,
            'group1_terms_sum_other_doc_count': 0,
            'group1_terms_doc_count{group1_terms="a"}': 2,
            'group1_terms_val_sum_value{group1_terms="a"}': 3.0,
            'group1_terms_group2_terms_doc_count_error_upper_bound{group1_terms="a"}': 0,
            'group1_terms_group2_terms_sum_other_doc_count{group1_terms="a"}': 0,
            'group1_terms_group2_terms_doc_count{group1_terms="a",group2_terms="a"}': 1,
            'group1_terms_group2_terms_val_sum_value{group1_terms="a",group2_terms="a"}': 1.0,
            'group1_terms_group2_terms_doc_count{group1_terms="a",group2_terms="b"}': 1,
            'group1_terms_group2_terms_val_sum_value{group1_terms="a",group2_terms="b"}': 2.0,
            'group1_terms_doc_count{group1_terms="b"}': 1,
            'group1_terms_val_sum_value{group1_terms="b"}': 3.0,
            'group1_terms_group2_terms_doc_count_error_upper_bound{group1_terms="b"}': 0,
            'group1_terms_group2_terms_sum_other_doc_count{group1_terms="b"}': 0,
            'group1_terms_group2_terms_doc_count{group1_terms="b",group2_terms="b"}': 1,
            'group1_terms_group2_terms_val_sum_value{group1_terms="b",group2_terms="b"}': 3.0,
        }
        result = convert_result(parse_response(response))
        self.assertEqual(result, expected)

if __name__ == '__main__':
    unittest.main()
