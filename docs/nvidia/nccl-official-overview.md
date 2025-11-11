# NVIDIA NCCL Documentation: Nccl - Overview

**Source**: https://docs.nvidia.com/deeplearning/nccl/user-guide/docs/overview.html
**Converted**: 2025-11-10
**Version**: NCCL 2.28.6

---

<div class="wy-grid-for-nav">

<div class="wy-side-scroll">

<div class="wy-side-nav-search">

[NCCL](index.html)

<div class="version">

[2.28](https://docs.nvidia.com/deeplearning/sdk/nccl-archived/index.html)

</div>

<div role="search">

</div>

</div>

<div class="wy-menu wy-menu-vertical" data-spy="affix" role="navigation" aria-label="main navigation">

  - [Overview of NCCL](#)
  - [Setup](setup.html)
  - [Using NCCL](usage.html)
      - [Creating a Communicator](usage/communicators.html)
          - [Creating a communicator with options](usage/communicators.html#creating-a-communicator-with-options)
          - [Creating a communicator using multiple ncclUniqueIds](usage/communicators.html#creating-a-communicator-using-multiple-nccluniqueids)
          - [Shrinking a communicator](usage/communicators.html#shrinking-a-communicator)
          - [Creating more communicators](usage/communicators.html#creating-more-communicators)
          - [Using multiple NCCL communicators concurrently](usage/communicators.html#using-multiple-nccl-communicators-concurrently)
          - [Finalizing a communicator](usage/communicators.html#finalizing-a-communicator)
          - [Destroying a communicator](usage/communicators.html#destroying-a-communicator)
      - [Error handling and communicator abort](usage/communicators.html#error-handling-and-communicator-abort)
          - [Asynchronous errors and error handling](usage/communicators.html#asynchronous-errors-and-error-handling)
      - [Fault Tolerance](usage/communicators.html#fault-tolerance)
      - [Quality of Service](usage/communicators.html#quality-of-service)
      - [Collective Operations](usage/collectives.html)
          - [AllReduce](usage/collectives.html#allreduce)
          - [Broadcast](usage/collectives.html#broadcast)
          - [Reduce](usage/collectives.html#reduce)
          - [AllGather](usage/collectives.html#allgather)
          - [ReduceScatter](usage/collectives.html#reducescatter)
          - [AlltoAll](usage/collectives.html#alltoall)
          - [Gather](usage/collectives.html#gather)
          - [Scatter](usage/collectives.html#scatter)
      - [Data Pointers](usage/data.html)
      - [CUDA Stream Semantics](usage/streams.html)
          - [Mixing Multiple Streams within the same ncclGroupStart/End() group](usage/streams.html#mixing-multiple-streams-within-the-same-ncclgroupstart-end-group)
      - [Group Calls](usage/groups.html)
          - [Management Of Multiple GPUs From One Thread](usage/groups.html#management-of-multiple-gpus-from-one-thread)
          - [Aggregated Operations (2.2 and later)](usage/groups.html#aggregated-operations-2-2-and-later)
          - [Group Operation Ordering Semantics](usage/groups.html#group-operation-ordering-semantics)
          - [Nonblocking Group Operation](usage/groups.html#nonblocking-group-operation)
      - [Point-to-point communication](usage/p2p.html)
          - [Sendrecv](usage/p2p.html#sendrecv)
          - [One-to-all (scatter)](usage/p2p.html#one-to-all-scatter)
          - [All-to-one (gather)](usage/p2p.html#all-to-one-gather)
          - [All-to-all](usage/p2p.html#all-to-all)
          - [Neighbor exchange](usage/p2p.html#neighbor-exchange)
      - [Thread Safety](usage/threadsafety.html)
      - [In-place Operations](usage/inplace.html)
      - [Using NCCL with CUDA Graphs](usage/cudagraph.html)
      - [User Buffer Registration](usage/bufferreg.html)
          - [NVLink Sharp Buffer Registration](usage/bufferreg.html#nvlink-sharp-buffer-registration)
          - [IB Sharp Buffer Registration](usage/bufferreg.html#ib-sharp-buffer-registration)
          - [General Buffer Registration](usage/bufferreg.html#general-buffer-registration)
          - [Buffer Registration and PXN](usage/bufferreg.html#buffer-registration-and-pxn)
          - [Memory Allocator](usage/bufferreg.html#memory-allocator)
          - [Window Registration](usage/bufferreg.html#window-registration)
          - [Zero-CTA Optimization](usage/bufferreg.html#zero-cta-optimization)
      - [Device-Initiated Communication](usage/deviceapi.html)
          - [Device API](usage/deviceapi.html#device-api)
          - [Host-Side Setup](usage/deviceapi.html#host-side-setup)
          - [Simple LSA Kernel](usage/deviceapi.html#simple-lsa-kernel)
          - [Multimem Device Kernel](usage/deviceapi.html#multimem-device-kernel)
          - [Thread Groups](usage/deviceapi.html#thread-groups)
          - [Teams](usage/deviceapi.html#teams)
          - [GIN Device Kernel](usage/deviceapi.html#gin-device-kernel)
  - [NCCL API](api.html)
      - [Communicator Creation and Management Functions](api/comms.html)
          - [ncclGetLastError](api/comms.html#ncclgetlasterror)
          - [ncclGetErrorString](api/comms.html#ncclgeterrorstring)
          - [ncclGetVersion](api/comms.html#ncclgetversion)
          - [ncclGetUniqueId](api/comms.html#ncclgetuniqueid)
          - [ncclCommInitRank](api/comms.html#ncclcomminitrank)
          - [ncclCommInitAll](api/comms.html#ncclcomminitall)
          - [ncclCommInitRankConfig](api/comms.html#ncclcomminitrankconfig)
          - [ncclCommInitRankScalable](api/comms.html#ncclcomminitrankscalable)
          - [ncclCommSplit](api/comms.html#ncclcommsplit)
          - [ncclCommShrink](api/comms.html#ncclcommshrink)
          - [ncclCommFinalize](api/comms.html#ncclcommfinalize)
          - [ncclCommRevoke](api/comms.html#ncclcommrevoke)
          - [ncclCommDestroy](api/comms.html#ncclcommdestroy)
          - [ncclCommAbort](api/comms.html#ncclcommabort)
          - [ncclCommGetAsyncError](api/comms.html#ncclcommgetasyncerror)
          - [ncclCommCount](api/comms.html#ncclcommcount)
          - [ncclCommCuDevice](api/comms.html#ncclcommcudevice)
          - [ncclCommUserRank](api/comms.html#ncclcommuserrank)
          - [ncclCommRegister](api/comms.html#ncclcommregister)
          - [ncclCommDeregister](api/comms.html#ncclcommderegister)
          - [ncclCommWindowRegister](api/comms.html#ncclcommwindowregister)
          - [ncclCommWindowDeregister](api/comms.html#ncclcommwindowderegister)
          - [ncclMemAlloc](api/comms.html#ncclmemalloc)
          - [ncclMemFree](api/comms.html#ncclmemfree)
      - [Collective Communication Functions](api/colls.html)
          - [ncclAllReduce](api/colls.html#ncclallreduce)
          - [ncclBroadcast](api/colls.html#ncclbroadcast)
          - [ncclReduce](api/colls.html#ncclreduce)
          - [ncclAllGather](api/colls.html#ncclallgather)
          - [ncclReduceScatter](api/colls.html#ncclreducescatter)
          - [ncclAlltoAll](api/colls.html#ncclalltoall)
          - [ncclGather](api/colls.html#ncclgather)
          - [ncclScatter](api/colls.html#ncclscatter)
      - [Group Calls](api/group.html)
          - [ncclGroupStart](api/group.html#ncclgroupstart)
          - [ncclGroupEnd](api/group.html#ncclgroupend)
          - [ncclGroupSimulateEnd](api/group.html#ncclgroupsimulateend)
      - [Point To Point Communication Functions](api/p2p.html)
          - [ncclSend](api/p2p.html#ncclsend)
          - [ncclRecv](api/p2p.html#ncclrecv)
      - [Types](api/types.html)
          - [ncclComm\_t](api/types.html#ncclcomm-t)
          - [ncclResult\_t](api/types.html#ncclresult-t)
          - [ncclDataType\_t](api/types.html#nccldatatype-t)
          - [ncclRedOp\_t](api/types.html#ncclredop-t)
          - [ncclScalarResidence\_t](api/types.html#ncclscalarresidence-t)
          - [ncclConfig\_t](api/types.html#ncclconfig-t)
          - [ncclSimInfo\_t](api/types.html#ncclsiminfo-t)
          - [ncclWindow\_t](api/types.html#ncclwindow-t)
      - [User Defined Reduction Operators](api/ops.html)
          - [ncclRedOpCreatePreMulSum](api/ops.html#ncclredopcreatepremulsum)
          - [ncclRedOpDestroy](api/ops.html#ncclredopdestroy)
      - [NCCL API Supported Flags](api/flags.html)
          - [Window Registration Flags](api/flags.html#window-registration-flags)
          - [NCCL Communicator CTA Policy Flags](api/flags.html#nccl-communicator-cta-policy-flags)
          - [Communicator Shrink Flags](api/flags.html#communicator-shrink-flags)
      - [Device API](api/device.html)
          - [Host-Side Setup](api/device.html#host-side-setup)
              - [ncclDevComm](api/device.html#nccldevcomm)
              - [ncclDevCommCreate](api/device.html#nccldevcommcreate)
              - [ncclDevCommDestroy](api/device.html#nccldevcommdestroy)
              - [ncclDevCommRequirements](api/device.html#nccldevcommrequirements)
          - [LSA](api/device.html#lsa)
              - [ncclLsaBarrierSession](api/device.html#nccllsabarriersession)
              - [ncclGetPeerPointer](api/device.html#ncclgetpeerpointer)
              - [ncclGetLsaPointer](api/device.html#ncclgetlsapointer)
              - [ncclGetLocalPointer](api/device.html#ncclgetlocalpointer)
          - [Multimem](api/device.html#multimem)
              - [ncclGetLsaMultimemPointer](api/device.html#ncclgetlsamultimempointer)
          - [GIN](api/device.html#gin)
              - [ncclGin](api/device.html#ncclgin)
              - [Signals and Counters](api/device.html#signals-and-counters)
              - [ncclGinBarrierSession](api/device.html#ncclginbarriersession)
  - [Migrating from NCCL 1 to NCCL 2](nccl1.html)
      - [Initialization](nccl1.html#initialization)
      - [Communication](nccl1.html#communication)
      - [Counts](nccl1.html#counts)
      - [In-place usage for AllGather and ReduceScatter](nccl1.html#in-place-usage-for-allgather-and-reducescatter)
      - [AllGather arguments order](nccl1.html#allgather-arguments-order)
      - [Datatypes](nccl1.html#datatypes)
      - [Error codes](nccl1.html#error-codes)
  - [Examples](examples.html)
      - [Communicator Creation and Destruction Examples](examples.html#communicator-creation-and-destruction-examples)
          - [Example 1: Single Process, Single Thread, Multiple Devices](examples.html#example-1-single-process-single-thread-multiple-devices)
          - [Example 2: One Device per Process or Thread](examples.html#example-2-one-device-per-process-or-thread)
          - [Example 3: Multiple Devices per Thread](examples.html#example-3-multiple-devices-per-thread)
          - [Example 4: Multiple communicators per device](examples.html#example-4-multiple-communicators-per-device)
      - [Communication Examples](examples.html#communication-examples)
          - [Example 1: One Device per Process or Thread](examples.html#example-1-one-device-per-process-or-thread)
          - [Example 2: Multiple Devices per Thread](examples.html#example-2-multiple-devices-per-thread)
  - [NCCL and MPI](mpi.html)
      - [API](mpi.html#api)
          - [Using multiple devices per process](mpi.html#using-multiple-devices-per-process)
          - [ReduceScatter operation](mpi.html#reducescatter-operation)
          - [Send and Receive counts](mpi.html#send-and-receive-counts)
          - [Other collectives and point-to-point operations](mpi.html#other-collectives-and-point-to-point-operations)
          - [In-place operations](mpi.html#in-place-operations)
      - [Using NCCL within an MPI Program](mpi.html#using-nccl-within-an-mpi-program)
          - [MPI Progress](mpi.html#mpi-progress)
          - [Inter-GPU Communication with CUDA-aware MPI](mpi.html#inter-gpu-communication-with-cuda-aware-mpi)
  - [Environment Variables](env.html)
      - [System configuration](env.html#system-configuration)
          - [NCCL\_SOCKET\_IFNAME](env.html#nccl-socket-ifname)
              - [Values accepted](env.html#values-accepted)
          - [NCCL\_SOCKET\_FAMILY](env.html#nccl-socket-family)
              - [Values accepted](env.html#id2)
          - [NCCL\_SOCKET\_RETRY\_CNT](env.html#nccl-socket-retry-cnt)
              - [Values accepted](env.html#id3)
          - [NCCL\_SOCKET\_RETRY\_SLEEP\_MSEC](env.html#nccl-socket-retry-sleep-msec)
              - [Values accepted](env.html#id4)
          - [NCCL\_SOCKET\_NTHREADS](env.html#nccl-socket-nthreads)
              - [Values accepted](env.html#id5)
          - [NCCL\_NSOCKS\_PERTHREAD](env.html#nccl-nsocks-perthread)
              - [Values accepted](env.html#id6)
          - [NCCL\_CROSS\_NIC](env.html#nccl-cross-nic)
              - [Values accepted](env.html#id7)
          - [NCCL\_IB\_HCA](env.html#nccl-ib-hca)
              - [Values accepted](env.html#id8)
          - [NCCL\_IB\_TIMEOUT](env.html#nccl-ib-timeout)
              - [Values accepted](env.html#id9)
          - [NCCL\_IB\_RETRY\_CNT](env.html#nccl-ib-retry-cnt)
              - [Values accepted](env.html#id10)
          - [NCCL\_IB\_GID\_INDEX](env.html#nccl-ib-gid-index)
              - [Values accepted](env.html#id11)
          - [NCCL\_IB\_ADDR\_FAMILY](env.html#nccl-ib-addr-family)
              - [Values accepted](env.html#id12)
          - [NCCL\_IB\_ADDR\_RANGE](env.html#nccl-ib-addr-range)
              - [Values accepted](env.html#id13)
          - [NCCL\_IB\_ROCE\_VERSION\_NUM](env.html#nccl-ib-roce-version-num)
              - [Values accepted](env.html#id14)
          - [NCCL\_IB\_SL](env.html#nccl-ib-sl)
              - [Values accepted](env.html#id15)
          - [NCCL\_IB\_TC](env.html#nccl-ib-tc)
              - [Values accepted](env.html#id16)
          - [NCCL\_IB\_FIFO\_TC](env.html#nccl-ib-fifo-tc)
              - [Values accepted](env.html#id17)
          - [NCCL\_IB\_RETURN\_ASYNC\_EVENTS](env.html#nccl-ib-return-async-events)
              - [Values accepted](env.html#id18)
          - [NCCL\_OOB\_NET\_ENABLE](env.html#nccl-oob-net-enable)
              - [Values accepted](env.html#id19)
          - [NCCL\_OOB\_NET\_IFNAME](env.html#nccl-oob-net-ifname)
              - [Values accepted](env.html#id20)
          - [NCCL\_UID\_STAGGER\_THRESHOLD](env.html#nccl-uid-stagger-threshold)
              - [Values accepted](env.html#id21)
          - [NCCL\_UID\_STAGGER\_RATE](env.html#nccl-uid-stagger-rate)
              - [Values accepted](env.html#id22)
          - [NCCL\_NET](env.html#nccl-net)
              - [Values accepted](env.html#id23)
          - [NCCL\_NET\_PLUGIN](env.html#nccl-net-plugin)
              - [Values accepted](env.html#id24)
          - [NCCL\_TUNER\_PLUGIN](env.html#nccl-tuner-plugin)
              - [Values accepted](env.html#id25)
          - [NCCL\_PROFILER\_PLUGIN](env.html#nccl-profiler-plugin)
              - [Values accepted](env.html#id26)
          - [NCCL\_ENV\_PLUGIN](env.html#nccl-env-plugin)
              - [Values accepted](env.html#id27)
          - [NCCL\_IGNORE\_CPU\_AFFINITY](env.html#nccl-ignore-cpu-affinity)
              - [Values accepted](env.html#id28)
          - [NCCL\_CONF\_FILE](env.html#nccl-conf-file)
              - [Values accepted](env.html#id29)
          - [NCCL\_DEBUG](env.html#nccl-debug)
              - [Values accepted](env.html#id31)
          - [NCCL\_DEBUG\_FILE](env.html#nccl-debug-file)
              - [Values accepted](env.html#id32)
          - [NCCL\_DEBUG\_SUBSYS](env.html#nccl-debug-subsys)
              - [Values accepted](env.html#id33)
          - [NCCL\_DEBUG\_TIMESTAMP\_FORMAT](env.html#nccl-debug-timestamp-format)
              - [Value accepted](env.html#value-accepted)
          - [NCCL\_DEBUG\_TIMESTAMP\_LEVELS](env.html#nccl-debug-timestamp-levels)
              - [Value accepted](env.html#id34)
          - [NCCL\_COLLNET\_ENABLE](env.html#nccl-collnet-enable)
              - [Value accepted](env.html#id35)
          - [NCCL\_COLLNET\_NODE\_THRESHOLD](env.html#nccl-collnet-node-threshold)
              - [Value accepted](env.html#id36)
          - [NCCL\_CTA\_POLICY](env.html#nccl-cta-policy)
              - [Value accepted](env.html#id37)
          - [NCCL\_NETDEVS\_POLICY](env.html#nccl-netdevs-policy)
              - [Value accepted](env.html#id38)
          - [NCCL\_TOPO\_FILE](env.html#nccl-topo-file)
              - [Value accepted](env.html#id39)
          - [NCCL\_TOPO\_DUMP\_FILE](env.html#nccl-topo-dump-file)
              - [Value accepted](env.html#id40)
          - [NCCL\_SET\_THREAD\_NAME](env.html#nccl-set-thread-name)
              - [Value accepted](env.html#id41)
      - [Debugging](env.html#debugging)
          - [NCCL\_P2P\_DISABLE](env.html#nccl-p2p-disable)
              - [Values accepted](env.html#id42)
          - [NCCL\_P2P\_LEVEL](env.html#nccl-p2p-level)
              - [Values accepted](env.html#id43)
              - [Integer Values (Legacy)](env.html#integer-values-legacy)
          - [NCCL\_P2P\_DIRECT\_DISABLE](env.html#nccl-p2p-direct-disable)
              - [Values accepted](env.html#id44)
          - [NCCL\_SHM\_DISABLE](env.html#nccl-shm-disable)
              - [Values accepted](env.html#id45)
          - [NCCL\_BUFFSIZE](env.html#nccl-buffsize)
              - [Values accepted](env.html#id46)
          - [NCCL\_NTHREADS](env.html#nccl-nthreads)
              - [Values accepted](env.html#id47)
          - [NCCL\_MAX\_NCHANNELS](env.html#nccl-max-nchannels)
              - [Values accepted](env.html#id48)
          - [NCCL\_MIN\_NCHANNELS](env.html#nccl-min-nchannels)
              - [Values accepted](env.html#id49)
          - [NCCL\_CHECKS\_DISABLE](env.html#nccl-checks-disable)
              - [Values accepted](env.html#id50)
          - [NCCL\_CHECK\_POINTERS](env.html#nccl-check-pointers)
              - [Values accepted](env.html#id51)
          - [NCCL\_LAUNCH\_MODE](env.html#nccl-launch-mode)
              - [Values accepted](env.html#id52)
          - [NCCL\_IB\_DISABLE](env.html#nccl-ib-disable)
              - [Values accepted](env.html#id53)
          - [NCCL\_IB\_AR\_THRESHOLD](env.html#nccl-ib-ar-threshold)
              - [Values accepted](env.html#id54)
          - [NCCL\_IB\_QPS\_PER\_CONNECTION](env.html#nccl-ib-qps-per-connection)
              - [Values accepted](env.html#id55)
          - [NCCL\_IB\_SPLIT\_DATA\_ON\_QPS](env.html#nccl-ib-split-data-on-qps)
              - [Values accepted](env.html#id56)
          - [NCCL\_IB\_CUDA\_SUPPORT](env.html#nccl-ib-cuda-support)
              - [Values accepted](env.html#id57)
          - [NCCL\_IB\_PCI\_RELAXED\_ORDERING](env.html#nccl-ib-pci-relaxed-ordering)
              - [Values accepted](env.html#id58)
          - [NCCL\_IB\_ADAPTIVE\_ROUTING](env.html#nccl-ib-adaptive-routing)
              - [Values accepted](env.html#id59)
          - [NCCL\_IB\_ECE\_ENABLE](env.html#nccl-ib-ece-enable)
              - [Values accepted](env.html#id60)
          - [NCCL\_MEM\_SYNC\_DOMAIN](env.html#nccl-mem-sync-domain)
              - [Values accepted](env.html#id61)
          - [NCCL\_CUMEM\_ENABLE](env.html#nccl-cumem-enable)
              - [Values accepted](env.html#id62)
          - [NCCL\_CUMEM\_HOST\_ENABLE](env.html#nccl-cumem-host-enable)
              - [Values accepted](env.html#id63)
          - [NCCL\_NET\_GDR\_LEVEL (formerly NCCL\_IB\_GDR\_LEVEL)](env.html#nccl-net-gdr-level-formerly-nccl-ib-gdr-level)
              - [Values accepted](env.html#id64)
              - [Integer Values (Legacy)](env.html#id65)
          - [NCCL\_NET\_GDR\_C2C](env.html#nccl-net-gdr-c2c)
              - [Values accepted](env.html#id66)
          - [NCCL\_NET\_GDR\_READ](env.html#nccl-net-gdr-read)
              - [Values accepted](env.html#id67)
          - [NCCL\_NET\_SHARED\_BUFFERS](env.html#nccl-net-shared-buffers)
              - [Value accepted](env.html#id68)
          - [NCCL\_NET\_SHARED\_COMMS](env.html#nccl-net-shared-comms)
              - [Value accepted](env.html#id69)
          - [NCCL\_SINGLE\_RING\_THRESHOLD](env.html#nccl-single-ring-threshold)
              - [Values accepted](env.html#id70)
          - [NCCL\_LL\_THRESHOLD](env.html#nccl-ll-threshold)
              - [Values accepted](env.html#id71)
          - [NCCL\_TREE\_THRESHOLD](env.html#nccl-tree-threshold)
              - [Values accepted](env.html#id72)
          - [NCCL\_ALGO](env.html#nccl-algo)
              - [Values accepted](env.html#id73)
          - [NCCL\_PROTO](env.html#nccl-proto)
              - [Values accepted](env.html#id74)
          - [NCCL\_NVB\_DISABLE](env.html#nccl-nvb-disable)
              - [Value accepted](env.html#id75)
          - [NCCL\_PXN\_DISABLE](env.html#nccl-pxn-disable)
              - [Value accepted](env.html#id76)
          - [NCCL\_P2P\_PXN\_LEVEL](env.html#nccl-p2p-pxn-level)
              - [Value accepted](env.html#id77)
          - [NCCL\_PXN\_C2C](env.html#nccl-pxn-c2c)
              - [Value accepted](env.html#id78)
          - [NCCL\_RUNTIME\_CONNECT](env.html#nccl-runtime-connect)
              - [Value accepted](env.html#id79)
          - [NCCL\_GRAPH\_REGISTER](env.html#nccl-graph-register)
              - [Value accepted](env.html#id81)
          - [NCCL\_LOCAL\_REGISTER](env.html#nccl-local-register)
              - [Value accepted](env.html#id82)
          - [NCCL\_LEGACY\_CUDA\_REGISTER](env.html#nccl-legacy-cuda-register)
              - [Value accepted](env.html#id83)
          - [NCCL\_WIN\_ENABLE](env.html#nccl-win-enable)
              - [Value accepted](env.html#id84)
          - [NCCL\_SET\_STACK\_SIZE](env.html#nccl-set-stack-size)
              - [Value accepted](env.html#id85)
          - [NCCL\_GRAPH\_MIXING\_SUPPORT](env.html#nccl-graph-mixing-support)
              - [Value accepted](env.html#id87)
          - [NCCL\_DMABUF\_ENABLE](env.html#nccl-dmabuf-enable)
              - [Value accepted](env.html#id88)
          - [NCCL\_P2P\_NET\_CHUNKSIZE](env.html#nccl-p2p-net-chunksize)
              - [Values accepted](env.html#id89)
          - [NCCL\_P2P\_LL\_THRESHOLD](env.html#nccl-p2p-ll-threshold)
              - [Values accepted](env.html#id90)
          - [NCCL\_ALLOC\_P2P\_NET\_LL\_BUFFERS](env.html#nccl-alloc-p2p-net-ll-buffers)
              - [Values accepted](env.html#id91)
          - [NCCL\_COMM\_BLOCKING](env.html#nccl-comm-blocking)
              - [Values accepted](env.html#id92)
          - [NCCL\_CGA\_CLUSTER\_SIZE](env.html#nccl-cga-cluster-size)
              - [Values accepted](env.html#id93)
          - [NCCL\_MAX\_CTAS](env.html#nccl-max-ctas)
              - [Values accepted](env.html#id94)
          - [NCCL\_MIN\_CTAS](env.html#nccl-min-ctas)
              - [Values accepted](env.html#id95)
          - [NCCL\_NVLS\_ENABLE](env.html#nccl-nvls-enable)
              - [Values accepted](env.html#id96)
          - [NCCL\_IB\_MERGE\_NICS](env.html#nccl-ib-merge-nics)
              - [Values accepted](env.html#id97)
          - [NCCL\_MNNVL\_ENABLE](env.html#nccl-mnnvl-enable)
              - [Values accepted](env.html#id98)
          - [NCCL\_MNNVL\_UUID](env.html#nccl-mnnvl-uuid)
              - [Values accepted](env.html#id99)
          - [NCCL\_MNNVL\_CLIQUE\_ID](env.html#nccl-mnnvl-clique-id)
              - [Values accepted](env.html#id100)
          - [NCCL\_RAS\_ENABLE](env.html#nccl-ras-enable)
              - [Values accepted](env.html#id101)
          - [NCCL\_RAS\_ADDR](env.html#nccl-ras-addr)
              - [Values accepted](env.html#id102)
          - [NCCL\_RAS\_TIMEOUT\_FACTOR](env.html#nccl-ras-timeout-factor)
              - [Values accepted](env.html#id103)
          - [NCCL\_LAUNCH\_ORDER\_IMPLICIT](env.html#nccl-launch-order-implicit)
              - [Values accepted](env.html#id105)
          - [NCCL\_LAUNCH\_RACE\_FATAL](env.html#nccl-launch-race-fatal)
              - [Values accepted](env.html#id106)
  - [Troubleshooting](troubleshooting.html)
      - [Errors](troubleshooting.html#errors)
      - [RAS](troubleshooting.html#ras)
          - [RAS](troubleshooting/ras.html)
              - [Principle of Operation](troubleshooting/ras.html#principle-of-operation)
              - [RAS Queries](troubleshooting/ras.html#ras-queries)
              - [Sample Output](troubleshooting/ras.html#sample-output)
      - [GPU Direct](troubleshooting.html#gpu-direct)
          - [GPU-to-GPU communication](troubleshooting.html#gpu-to-gpu-communication)
          - [GPU-to-NIC communication](troubleshooting.html#gpu-to-nic-communication)
          - [PCI Access Control Services (ACS)](troubleshooting.html#pci-access-control-services-acs)
      - [Topology detection](troubleshooting.html#topology-detection)
      - [Memory issues](troubleshooting.html#memory-issues)
          - [Shared memory](troubleshooting.html#shared-memory)
          - [Stack size](troubleshooting.html#stack-size)
          - [Unified Memory (UVM)](troubleshooting.html#unified-memory-uvm)
      - [Networking issues](troubleshooting.html#networking-issues)
          - [IP Network Interfaces](troubleshooting.html#ip-network-interfaces)
          - [IP Ports](troubleshooting.html#ip-ports)
          - [InfiniBand](troubleshooting.html#infiniband)
          - [RDMA over Converged Ethernet (RoCE)](troubleshooting.html#rdma-over-converged-ethernet-roce)

</div>

</div>

<div class="section wy-nav-content-wrap" data-toggle="wy-nav-shift">

** [NCCL](index.html)

<div class="wy-nav-content">

<div class="rst-content">

<div role="navigation" aria-label="breadcrumbs navigation">

  - [Docs](index.html) »
  - Overview of NCCL
  - [View page source](_sources/overview.rst.txt)

-----

</div>

<div class="document" role="main" itemscope="itemscope" itemtype="http://schema.org/Article">

<div itemprop="articleBody">

<div id="overview-of-nccl" class="section">

# Overview of NCCL[¶](#overview-of-nccl "Permalink to this headline")

The NVIDIA Collective Communications Library (NCCL, pronounced “Nickel”) is a library providing inter-GPU communication primitives that are topology-aware and can be easily integrated into applications.

NCCL implements both collective communication and point-to-point send/receive primitives. It is not a full-blown parallel programming framework; rather, it is a library focused on accelerating inter-GPU communication.

NCCL provides the following collective communication primitives :

  - AllReduce
  - Broadcast
  - Reduce
  - AllGather
  - ReduceScatter
  - AlltoAll
  - Gather
  - Scatter

Additionally, it allows for point-to-point send/receive communication which allows for scatter, gather, or all-to-all operations.

Tight synchronization between communicating processors is a key aspect of collective communication. CUDA based collectives would traditionally be realized through a combination of CUDA memory copy operations and CUDA kernels for local reductions. NCCL, on the other hand, implements each collective in a single kernel handling both communication and computation operations. This allows for fast synchronization and minimizes the resources needed to reach peak bandwidth.

NCCL conveniently removes the need for developers to optimize their applications for specific machines. NCCL provides fast collectives over multiple GPUs both within and across nodes. It supports a variety of interconnect technologies including PCIe, NVLINK, InfiniBand Verbs, and IP sockets.

Next to performance, ease of programming was the primary consideration in the design of NCCL. NCCL uses a simple C API, which can be easily accessed from a variety of programming languages. NCCL closely follows the popular collectives API defined by MPI (Message Passing Interface). Anyone familiar with MPI will thus find NCCL’s API very natural to use. In a minor departure from MPI, NCCL collectives take a “stream” argument which provides direct integration with the CUDA programming model. Finally, NCCL is compatible with virtually any multi-GPU parallelization model, for example:

  - single-threaded control of all GPUs
  - multi-threaded, for example, using one thread per GPU
  - multi-process, for example, MPI

NCCL has found great application in Deep Learning Frameworks, where the AllReduce collective is heavily used for neural network training. Efficient scaling of neural network training is possible with the multi-GPU and multi node communication provided by NCCL.

</div>

</div>

</div>

<div class="rst-footer-buttons" role="navigation" aria-label="footer navigation">

[Next <span class="fa fa-arrow-circle-right"></span>](setup.html "Setup") [<span class="fa fa-arrow-circle-left"></span> Previous](index.html "NVIDIA Collective Communication Library (NCCL) Documentation")

</div>

-----

<div role="contentinfo">

© Copyright 2020, NVIDIA Corporation

</div>

Built with [Sphinx](http://sphinx-doc.org/) using a [theme](https://github.com/rtfd/sphinx_rtd_theme) provided by [Read the Docs](https://readthedocs.org).

</div>

</div>

</div>

</div>
