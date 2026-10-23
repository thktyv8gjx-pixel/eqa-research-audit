import Foundation
import AVFoundation
import AppKit
import ImageIO
import UniformTypeIdentifiers

func stamp(_ t: CMTime) -> [String:Any] {
    return ["value":t.value,"timescale":t.timescale,"seconds":t.isNumeric ? t.seconds : NSNull(),"flags":t.flags.rawValue]
}
func writeJSON(_ x: Any, _ path: String) throws {
    try JSONSerialization.data(withJSONObject:x,options:[.prettyPrinted,.sortedKeys]).write(to:URL(fileURLWithPath:path),options:.withoutOverwriting)
}

@main struct Audit {
 static func main() async {
  do {
   let args=CommandLine.arguments
   let mode=args[1], input=args[2], output=args[3]
   let asset=AVURLAsset(url:URL(fileURLWithPath:input),options:[AVURLAssetPreferPreciseDurationAndTimingKey:true])
   let duration=try await asset.load(.duration)
   let tracks=try await asset.loadTracks(withMediaType:.video)
   guard let track=tracks.first else {throw NSError(domain:"Audit",code:1,userInfo:[NSLocalizedDescriptionKey:"No video track"])}
   let tr=try await track.load(.timeRange)
   let size=try await track.load(.naturalSize)
   let fps=try await track.load(.nominalFrameRate)
   let minDur=try await track.load(.minFrameDuration)
   let segments=try await track.load(.segments)
   let transform=try await track.load(.preferredTransform)
   var info:[String:Any]=["asset_duration":stamp(duration),"track_start":stamp(tr.start),"track_duration":stamp(tr.duration),"width":size.width,"height":size.height,"nominal_fps":fps,"min_frame_duration":stamp(minDur),"preferred_transform":[transform.a,transform.b,transform.c,transform.d,transform.tx,transform.ty],"segments":segments.map{["empty":$0.isEmpty,"source_start":stamp($0.timeMapping.source.start),"source_duration":stamp($0.timeMapping.source.duration),"target_start":stamp($0.timeMapping.target.start),"target_duration":stamp($0.timeMapping.target.duration)]}]
   if mode == "metadata" {
    let reader=try AVAssetReader(asset:asset)
    let trackout=AVAssetReaderTrackOutput(track:track,outputSettings:nil)
    trackout.alwaysCopiesSampleData=false;reader.add(trackout)
    guard reader.startReading() else {throw reader.error!}
    var lines="index,pts_value,pts_scale,pts_seconds,dts_value,dts_scale,dts_seconds,duration_seconds,sync\n"
    var i=0; var last = -Double.infinity;var monotonic=true
    while let sample=trackout.copyNextSampleBuffer() {
     let p=CMSampleBufferGetPresentationTimeStamp(sample),d=CMSampleBufferGetDecodeTimeStamp(sample),u=CMSampleBufferGetDuration(sample)
     if p.seconds<last {monotonic=false}; last=p.seconds
     let attachments=CMSampleBufferGetSampleAttachmentsArray(sample,createIfNecessary:false) as? [[CFString:Any]]
     let notsync=attachments?.first?[kCMSampleAttachmentKey_NotSync] as? Bool ?? false
     lines += "\(i),\(p.value),\(p.timescale),\(p.seconds),\(d.value),\(d.timescale),\(d.isNumeric ? String(d.seconds) : "NA"),\(u.seconds),\(!notsync)\n"; i += 1
    }
    info["sample_count"]=i;info["sample_output_pts_monotonic"]=monotonic; info["reader_status"]=reader.status.rawValue;info["reader_error"]=reader.error?.localizedDescription ?? NSNull()
    try lines.write(toFile:output+".csv",atomically:true,encoding:.utf8)
    try writeJSON(info,output+".json")
   } else if mode == "frames" {
    let data=try Data(contentsOf:URL(fileURLWithPath:args[4]))
    let targets=try JSONSerialization.jsonObject(with:data) as! [Double]
    guard targets.allSatisfy({$0>=0 && $0<=288.65}) else {throw NSError(domain:"Audit",code:2)}
    let gen=AVAssetImageGenerator(asset:asset)
    gen.appliesPreferredTrackTransform=true
    gen.maximumSize=CGSize(width:1280,height:1280)
    gen.requestedTimeToleranceBefore = .zero; gen.requestedTimeToleranceAfter = .zero
    var records=[[String:Any]]()
    for (idx,target) in targets.enumerated() {
     try autoreleasepool {
      let requested=CMTime(seconds:target,preferredTimescale:30000)
      var actual=CMTime.zero
      let cg=try gen.copyCGImage(at:requested,actualTime:&actual)
      guard actual.isNumeric && actual.seconds>=0 && actual.seconds<=288.65 else {throw NSError(domain:"Audit",code:3,userInfo:[NSLocalizedDescriptionKey:"Future/out-of-prefix frame rejected"])}
      let file=String(format:"frame_%04d_%010.5f.jpg",idx,actual.seconds)
      let url=URL(fileURLWithPath:output).appendingPathComponent(file)
      guard !FileManager.default.fileExists(atPath:url.path) else {throw NSError(domain:"Audit",code:4)}
      guard let dest=CGImageDestinationCreateWithURL(url as CFURL,UTType.jpeg.identifier as CFString,1,nil) else {throw NSError(domain:"Audit",code:5)}
      CGImageDestinationAddImage(dest,cg,[kCGImageDestinationLossyCompressionQuality:0.88] as CFDictionary)
      guard CGImageDestinationFinalize(dest) else {throw NSError(domain:"Audit",code:6)}
      records.append(["file":file,"requested":stamp(requested),"actual":stamp(actual),"width":cg.width,"height":cg.height])
     }
    }
    info["frames"]=records
    try writeJSON(info,output+"/frames.json")
   } else if mode == "decode_prefix" {
    let reader=try AVAssetReader(asset:asset)
    reader.timeRange=CMTimeRange(start:.zero,duration:CMTime(value:28865,timescale:100))
    let trackout=AVAssetReaderTrackOutput(track:track,outputSettings:[kCVPixelBufferPixelFormatTypeKey as String:kCVPixelFormatType_32BGRA])
    trackout.alwaysCopiesSampleData=false;reader.add(trackout)
    guard reader.startReading() else {throw reader.error!}
    var count=0;var first=Double.infinity;var last = -Double.infinity;var future=0;var nonmonotonic=0
    while let sample=trackout.copyNextSampleBuffer() {
     let time=CMSampleBufferGetPresentationTimeStamp(sample).seconds
     if time>288.65 {future += 1;continue}
     if time<last {nonmonotonic += 1};first=min(first,time);last=max(last,time);count += 1
    }
    info["decoded_prefix_frames"]=count;info["first_pts_seconds"]=first;info["last_pts_seconds"]=last;info["future_samples_rejected"]=future;info["nonmonotonic_pts"]=nonmonotonic;info["reader_status"]=reader.status.rawValue;info["reader_error"]=reader.error?.localizedDescription ?? NSNull()
    try writeJSON(info,output)
   } else {throw NSError(domain:"Audit",code:9)}
   print("OK \(mode)")
  } catch {
   fputs("AUDIT_ERROR: \(error)\n",stderr);exit(1)
  }
 }
}
