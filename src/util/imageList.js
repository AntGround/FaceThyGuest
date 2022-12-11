class RollingList
{
    constructor(size){
        super()
        this.size = size;
        this.dataList = []; 
    }

    add(ele) {
        if(this.dataList.length === (this.size-1))
            this.dataList.shift()
        this.dataList.push(ele)
    }
}