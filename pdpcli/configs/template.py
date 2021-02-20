from pdpcli.stages import PdpipelineStage
from pdpcli.data.data_reader import DataReader
from pdpcli.data.data_writer import DataWriter


class ConfigTemplate:
    def __init__(self,
                 pipeline: PdpipelineStage,
                 reader: DataReader = None,
                 writer: DataWriter = None) -> None:
        self.pipeline = pipeline
        self.reader = reader
        self.writer = writer
