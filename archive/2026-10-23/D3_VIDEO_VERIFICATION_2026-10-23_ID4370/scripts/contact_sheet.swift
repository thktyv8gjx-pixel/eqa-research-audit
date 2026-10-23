import Foundation
import AppKit
import ImageIO
import UniformTypeIdentifiers

let args=CommandLine.arguments
let folder=URL(fileURLWithPath:args[1])
let prefix=args[2]
let json=try JSONSerialization.jsonObject(with:Data(contentsOf:folder.appendingPathComponent("frames.json"))) as! [String:Any]
let frames=json["frames"] as! [[String:Any]]
let perPage=12, cols=4, tile=384, caption=34
for start in stride(from:0,to:frames.count,by:perPage) {
 let entries=Array(frames[start..<min(start+perPage,frames.count)])
 let rows=(entries.count+cols-1)/cols
 let width=cols*tile, height=rows*(tile+caption)
 let canvas=NSImage(size:NSSize(width:width,height:height))
 canvas.lockFocus()
 NSColor.white.setFill();NSRect(x:0,y:0,width:width,height:height).fill()
 for (i,entry) in entries.enumerated() {
  let path=folder.appendingPathComponent(entry["file"] as! String)
  let image=NSImage(contentsOf:path)!
  let col=i%cols, row=i/cols
  let x=col*tile, y=height-(row+1)*(tile+caption)
  image.draw(in:NSRect(x:x,y:y+caption,width:tile,height:tile),from:.zero,operation:.sourceOver,fraction:1)
  let actual=entry["actual"] as! [String:Any], time=actual["seconds"] as! Double
  let label=String(format:"#%03d   actual PTS %.5f s",start+i,time)
  (label as NSString).draw(at:NSPoint(x:x+8,y:y+8),withAttributes:[.font:NSFont.monospacedSystemFont(ofSize:15,weight:.regular),.foregroundColor:NSColor.black])
 }
 canvas.unlockFocus()
 var rect=NSRect(origin:.zero,size:canvas.size)
 let cg=canvas.cgImage(forProposedRect:&rect,context:nil,hints:nil)!
 let out=folder.appendingPathComponent(String(format:"%@_%02d.jpg",prefix,start/perPage))
 guard !FileManager.default.fileExists(atPath:out.path) else {fatalError("No overwrite")}
 let dest=CGImageDestinationCreateWithURL(out as CFURL,UTType.jpeg.identifier as CFString,1,nil)!
 CGImageDestinationAddImage(dest,cg,[kCGImageDestinationLossyCompressionQuality:0.90] as CFDictionary)
 guard CGImageDestinationFinalize(dest) else {fatalError("Write failed")}
}
print("SHEETS_OK \(frames.count) frames")
