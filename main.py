import os
import math
from PIL import Image
import json
from concurrent.futures import ProcessPoolExecutor
from functools import cache
import traceback

@cache
def getDistance(dx:int, dy:int)->float:
    return (dx**2+dy**2)**0.5

@cache
def getDifference(c1, c2)->int:
    r1, g1, b1 = c1
    r2, g2, b2 = c2
    return abs(r1-r2)+abs(g1-g2)+abs(b1-b2)
def calculateClosest(ip, ap, x:int, y:int, seekRange:int, width:int, height:int, round:bool):
    try:
        current_color = ip[x, y]
        currentContestant = ap[x, y]
        currentDiff = getDifference(current_color, currentContestant)
        for i in range(x-seekRange, x+seekRange+1):
            if i<0 or i>width-1: continue
            for j in range(y-seekRange, y+seekRange+1):
                if j<0 or j>height-1: continue
                if not round and getDistance(i-x, j-y)>seekRange: continue
                diff = getDifference(current_color, ap[i, j])
                if diff<currentDiff: 
                    currentDiff=diff
                    currentContestant=ap[i,j]
        return currentContestant
    except Exception as e:
        traceback.print_exc()
        return (0,0,0)
def calculateArea(args):
    ipath, apath, start, end, seekRange, round = args
    input = Image.open(ipath).convert("RGB")
    target_size = input.size
    attunement = Image.open(apath).convert("RGB")
    attunement = attunement.resize(target_size, Image.Resampling.LANCZOS)
    width, height = target_size
    result = []
    ip=input.load()
    if ip is None:
        return []
    ap=attunement.load()
    if ap is None:
        return []
    try:
        for x in range(start, end):
            for y in range(0, height):
                result.append(calculateClosest(ip, ap, x, y, seekRange, width, height, round))
        print("!!!Finished thread")
        return result
    except Exception as e:
        traceback.print_exc()
        return []
    
def attune(inputPath:str, attunementPath: str, seekRange:int=16, round:bool=False, multithread:bool=True, num_threads:int=0)->Image.Image|None:
    input = Image.open(inputPath).convert("RGB")
    attunement = Image.open(attunementPath).convert("RGB")
    target_size = input.size
    attunement = attunement.resize(target_size, Image.Resampling.LANCZOS)
    width, height = target_size
    if multithread:
        num_cores = (os.cpu_count() or 4) if num_threads<1 else num_threads
        print(num_cores)
        tasks = []
        chunk_size = int(math.ceil(width/num_cores))
        for i in range(num_cores):
            s=max(i*chunk_size, 0)
            e=min((i+1)*chunk_size, width)
            tasks.append((inputPath, attunementPath, s, e, seekRange, round))
        with ProcessPoolExecutor(max_workers=num_cores) as executor:
            results = list(executor.map(calculateArea, tasks))
        final_img = Image.new("RGB", target_size)
        fpixels=final_img.load()
        if fpixels is None:
            return None
        compressed=[]
        for result in results:
            compressed.extend(result) # type: ignore
        for x in range(width):
            for y in range(height):
                fpixels[x,y]=compressed[x*height+y]
        input.close()
        attunement.close()
        return final_img
    else:
        width, height = target_size
        final_img = Image.new("RGB", target_size)
        fpixels=final_img.load()
        if fpixels is None:
            return None
        ip=input.load()
        if ip is None:
            return None
        ap=attunement.load()
        if ap is None:
            return None
        for x in range(width):
            for y in range(height):
                fpixels[x,y]=calculateClosest(ip, ap, x, y, seekRange, width, height, round)
        return final_img
                

def main():
    with open("config.json", "r+", encoding="UTF-8") as file:
        config = json.loads(file.read())
        file.close()
        
    attunementPath = config["attunementFile"]
    inputPath = config["input"]
    outputPath = config["output"]
    seekRange = config["seekRange"]
    round = config["round"]
    img = attune(inputPath, attunementPath, seekRange, round)
    if img is None:
        return
    img.save(outputPath)
    img.close()

if __name__=="__main__":
    main()