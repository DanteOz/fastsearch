from dagster import DynamicPartitionsDefinition

video_partition_def = DynamicPartitionsDefinition(name="video_id")
