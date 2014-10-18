import FWCore.ParameterSet.Config as cms
process = cms.Process("HIGHPTSKIM")

process.load('Configuration.StandardSequences.Services_cff')
process.load('FWCore.MessageService.MessageLogger_cfi')
process.load('Configuration.EventContent.EventContentHeavyIons_cff')

import FWCore.ParameterSet.VarParsing as VarParsing

ivars = VarParsing.VarParsing('python')
ivars.inputFiles = '/lio/lfs/cms/store/hidata/HIRun2011/HIHighPt/RECO/14Mar2014-v2/00030/E225A85D-99C3-E311-B632-FA163EF2B3E5.root'
ivars.parseArguments()


process.source = cms.Source("PoolSource",
   fileNames = cms.untracked.vstring(
ivars.inputFiles
)
)

# =============== Other Statements =====================
process.maxEvents = cms.untracked.PSet(input = cms.untracked.int32(500))
process.options = cms.untracked.PSet(wantSummary = cms.untracked.bool(False))
process.MessageLogger.cerr.FwkReport.reportEvery = 100

#Trigger Selection
### Comment out for the timing being assuming running on secondary dataset with trigger bit selected already
import HLTrigger.HLTfilters.hltHighLevel_cfi
process.hltHIHighPt = HLTrigger.HLTfilters.hltHighLevel_cfi.hltHighLevel.clone()
process.hltHIHighPt.HLTPaths = ['HLT_HIDoublePhoton15_*','HLT_HIJet80_*','HLT_HISinglePhoton40_*'] # for allphysics
process.hltHIHighPt.andOr = cms.bool(True)
process.hltHIHighPt.throw = cms.bool(False)

process.eventFilter_step = cms.Path( process.hltHIHighPt )

process.output = cms.OutputModule("PoolOutputModule",
    outputCommands = process.RECOEventContent.outputCommands,
    fileName = cms.untracked.string('hiHighPt.root'),
    SelectEvents = cms.untracked.PSet(SelectEvents = cms.vstring('eventFilter_step')),
    dataset = cms.untracked.PSet(
      dataTier = cms.untracked.string('RECO'),
      filterName = cms.untracked.string('hiHighPt'))
)

process.output_step = cms.EndPath(process.output)

process.schedule = cms.Schedule(
    process.eventFilter_step,
    process.output_step
)

